#!/usr/bin/env python3
"""Clone every project repo into runs/<run>/<CODE>/repo, completely.

For each project row in projects.json:
  * git clone (all branches + tags), borrowing objects from the local
    github-backup mirror via --reference/--dissociate so little is downloaded
  * recursive submodule init, each one also seeded from its backup mirror
  * git lfs fetch --all + checkout
  * every release asset (GitHub via gh, GitLab via its API) into releases/

Idempotent: re-running fetches into existing clones and skips downloaded
assets.  Per-project detail goes to <dir>/clone.log and clone_status.json;
one "EVT" line per project start/finish goes to stdout for progress tracking.
"""
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1]
BACKUP = Path("/backups/github")
WORKERS = 8
MAX_SUBMODULE_DEPTH = 8

ENV = dict(os.environ)
ENV.update({
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_LFS_SKIP_SMUDGE": "1",
    # public repos listed with ssh URLs clone fine anonymously over https
    "GIT_CONFIG_COUNT": "2",
    "GIT_CONFIG_KEY_0": "url.https://github.com/.insteadOf",
    "GIT_CONFIG_VALUE_0": "git@github.com:",
    "GIT_CONFIG_KEY_1": "url.https://gitlab.com/.insteadOf",
    "GIT_CONFIG_VALUE_1": "git@gitlab.com:",
})

_print_lock = threading.Lock()
_dir_cache = {}
_dir_lock = threading.Lock()


def evt(msg):
    with _print_lock:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "EVT", msg, flush=True)


def ci_child(parent, name):
    """Case-insensitive lookup of `name` inside directory `parent`."""
    with _dir_lock:
        if parent not in _dir_cache:
            try:
                _dir_cache[parent] = {n.lower(): n for n in os.listdir(parent)}
            except OSError:
                _dir_cache[parent] = {}
        real = _dir_cache[parent].get(name.lower())
    return parent / real if real else None


def find_mirror(url):
    """Map a clone URL onto its github-backup mirror directory, if any."""
    m = re.match(r"^(?:https?://|git://|ssh://git@|git@)([^/:]+)[:/](.+?)/?$", url.strip())
    if not m:
        return None
    host, path = m.group(1).lower(), re.sub(r"\.git$", "", m.group(2))
    cur = BACKUP / host
    parts = path.split("/")
    for i, part in enumerate(parts):
        cur = ci_child(cur, part + (".git" if i == len(parts) - 1 else ""))
        if cur is None:
            return None
    return cur if (cur / "objects").is_dir() else None


class Job:
    def __init__(self, project, canonical):
        self.p = project
        self.dir = RUNS / project["run"] / project["code"]
        self.repo = self.dir / "repo"
        self.canonical = canonical
        self.status = {"run": project["run"], "code": project["code"], "errors": [],
                       "submodules": [], "releases": []}
        self.log = None

    def run(self, cmd, cwd=None, check=True):
        self.log.write("\n$ %s   (cwd=%s)\n" % (" ".join(map(str, cmd)), cwd or "."))
        self.log.flush()
        r = subprocess.run(list(map(str, cmd)), cwd=cwd, env=ENV, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True, errors="replace")
        self.log.write(r.stdout)
        self.log.write("[exit %d]\n" % r.returncode)
        self.log.flush()
        if check and r.returncode != 0:
            tail = " | ".join(r.stdout.strip().splitlines()[-3:])
            self.status["errors"].append("%s: exit %d: %s" % (" ".join(map(str, cmd[:4])), r.returncode, tail))
        return r

    # -- git ---------------------------------------------------------------
    def clone(self):
        r = self.p["repo"]
        url = "https://%s/%s.git" % (r["host"], self.canonical)
        self.status["url"] = url
        mirror = find_mirror(url)
        self.status["mirror"] = str(mirror) if mirror else None
        if (self.repo / ".git").exists():
            self.run(["git", "fetch", "--all", "--tags", "--force"], cwd=self.repo)
        else:
            cmd = ["git", "clone"]
            if mirror:
                cmd += ["--reference", mirror, "--dissociate"]
            if r["branch"]:
                cmd += ["--branch", r["branch"]]
            cmd += [url, self.repo]
            if self.run(cmd).returncode != 0:
                return False
        g = lambda *a: self.run(["git", *a], cwd=self.repo, check=False).stdout.strip()
        self.status["head"] = g("rev-parse", "HEAD")
        self.status["branch"] = g("rev-parse", "--abbrev-ref", "HEAD")
        self.status["head_date"] = g("log", "-1", "--format=%cI")
        self.status["remote_branches"] = len(g("for-each-ref", "refs/remotes/origin").splitlines())
        self.status["tags"] = len(g("tag").splitlines())
        return True

    def submodules(self, repo, origin_url, depth=0, prefix=""):
        if not (repo / ".gitmodules").exists():
            return
        if depth > MAX_SUBMODULE_DEPTH:
            self.status["errors"].append("submodule depth limit at %s" % prefix)
            return
        cfg = self.run(["git", "config", "-f", ".gitmodules", "--get-regexp",
                        r"^submodule\..*\.(path|url)$"], cwd=repo, check=False).stdout
        subs = {}
        for line in cfg.splitlines():
            key, _, val = line.partition(" ")
            name, field = key[len("submodule."):].rsplit(".", 1)
            subs.setdefault(name, {})[field] = val.strip()
        for name, s in subs.items():
            path, url = s.get("path"), s.get("url")
            if not path or not url:
                continue
            if url.startswith("."):  # relative to the superproject's remote
                url = urllib.parse.urljoin(re.sub(r"(\.git)?/?$", "/", origin_url), url)
            mirror = find_mirror(url)
            cmd = ["git", "submodule", "update", "--init"]
            if mirror:
                cmd += ["--reference", mirror, "--dissociate"]
            cmd += ["--", path]
            r = self.run(cmd, cwd=repo, check=False)
            ok = r.returncode == 0
            sub_dir = repo / path
            head = ""
            if ok:
                head = self.run(["git", "rev-parse", "HEAD"], cwd=sub_dir, check=False).stdout.strip()
            else:
                tail = " | ".join(r.stdout.strip().splitlines()[-2:])
                self.status["errors"].append("submodule %s%s (%s): %s" % (prefix, path, url, tail))
            self.status["submodules"].append({"path": prefix + path, "url": url, "ok": ok,
                                              "seeded_from_mirror": bool(mirror), "head": head})
            if ok:
                self.submodules(sub_dir, url, depth + 1, prefix + path + "/")

    def lfs(self):
        attrs = self.run(["git", "grep", "-l", "filter=lfs", "HEAD", "--", ".gitattributes",
                          "**/.gitattributes"], cwd=self.repo, check=False).stdout.strip()
        self.status["lfs"] = bool(attrs)
        if attrs:
            self.run(["git", "lfs", "fetch", "--all"], cwd=self.repo)
            self.run(["git", "lfs", "checkout"], cwd=self.repo)
            ls = self.run(["git", "lfs", "ls-files"], cwd=self.repo, check=False).stdout.splitlines()
            self.status["lfs_files"] = len(ls)
            self.status["lfs_missing"] = sum(1 for l in ls if " - " in l)
        if self.status["submodules"]:
            self.run(["git", "submodule", "foreach", "--recursive",
                      "if git grep -q filter=lfs HEAD -- .gitattributes 2>&1; then git lfs pull; fi"],
                     cwd=self.repo, check=False)

    # -- releases ----------------------------------------------------------
    def releases_github(self):
        r = self.run(["gh", "api", "--paginate", "--slurp", "repos/%s/releases" % self.canonical], check=False)
        try:
            rels = [x for page in json.loads(r.stdout[:r.stdout.rindex("]") + 1]) for x in page]
        except ValueError:
            self.status["errors"].append("could not list releases")
            return
        (self.dir / "releases.json").write_text(json.dumps(rels, indent=1))
        for rel in rels:
            assets = rel.get("assets", [])
            entry = {"tag": rel["tag_name"], "name": rel.get("name"), "published": rel.get("published_at"),
                     "assets": [{"name": a["name"], "size": a["size"]} for a in assets]}
            self.status["releases"].append(entry)
            if not assets:
                continue
            out = self.dir / "releases" / rel["tag_name"].replace("/", "_")
            out.mkdir(parents=True, exist_ok=True)
            self.run(["gh", "release", "download", rel["tag_name"], "-R", self.canonical,
                      "-D", out, "--skip-existing"])

    def releases_gitlab(self):
        api = "https://gitlab.com/api/v4/projects/%s/releases" % urllib.parse.quote(self.canonical, safe="")
        try:
            rels = json.load(urllib.request.urlopen(api, timeout=60))
        except Exception as e:  # noqa: BLE001 - recorded, not fatal
            self.status["errors"].append("gitlab releases: %s" % e)
            return
        (self.dir / "releases.json").write_text(json.dumps(rels, indent=1))
        for rel in rels:
            links = rel.get("assets", {}).get("links", [])
            self.status["releases"].append({"tag": rel["tag_name"], "name": rel.get("name"),
                                            "published": rel.get("released_at"),
                                            "assets": [{"name": l["name"]} for l in links]})
            out = self.dir / "releases" / rel["tag_name"].replace("/", "_")
            for l in links:
                out.mkdir(parents=True, exist_ok=True)
                dest = out / l["name"].replace("/", "_")
                if not dest.exists():
                    self.run(["curl", "-sS", "-L", "--fail", "-o", dest, l.get("direct_asset_url") or l["url"]])

    # -- driver ------------------------------------------------------------
    def go(self):
        t0 = time.time()
        tag = "%s/%s" % (self.p["run"], self.p["code"])
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "project.json").write_text(json.dumps(self.p, indent=1) + "\n")
        if not self.p["repo"]:
            self.status["skipped"] = "no repository listed"
            (self.dir / "clone_status.json").write_text(json.dumps(self.status, indent=1) + "\n")
            evt("done %s norepo" % tag)
            return self.status
        evt("start %s %s" % (tag, self.canonical))
        with (self.dir / "clone.log").open("a") as self.log:
            self.log.write("\n===== %s =====\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
            try:
                if self.clone():
                    self.submodules(self.repo, self.status["url"])
                    self.lfs()
                if self.p["repo"]["host"] == "github.com":
                    self.releases_github()
                elif self.p["repo"]["host"] == "gitlab.com":
                    self.releases_gitlab()
            except Exception as e:  # noqa: BLE001 - one project must not stop the rest
                self.status["errors"].append("exception: %r" % e)
        self.status["seconds"] = round(time.time() - t0, 1)
        (self.dir / "clone_status.json").write_text(json.dumps(self.status, indent=1) + "\n")
        evt("done %s %s errors=%d subs=%d releases=%d secs=%d" % (
            tag, "ok" if not self.status["errors"] else "ERRORS", len(self.status["errors"]),
            len(self.status["submodules"]), len(self.status["releases"]), self.status["seconds"]))
        return self.status


def main():
    projects = json.load((RUNS / "projects.json").open())
    gh = json.load((RUNS / "github_state.json").open())["repos"]
    only = set(sys.argv[1:])
    jobs = []
    for p in projects:
        if only and "%s/%s" % (p["run"], p["code"]) not in only:
            continue
        canonical = None
        if p["repo"]:
            canonical = p["repo"]["path"]
            if p["repo"]["host"] == "github.com":
                canonical = gh[canonical]["nameWithOwner"]
        jobs.append(Job(p, canonical))
    evt("begin total=%d" % len(jobs))
    with concurrent.futures.ThreadPoolExecutor(WORKERS) as ex:
        results = list(ex.map(lambda j: j.go(), jobs))
    bad = [r for r in results if r["errors"]]
    evt("end total=%d with_errors=%d" % (len(results), len(bad)))


if __name__ == "__main__":
    main()
