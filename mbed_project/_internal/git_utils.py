#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Wrappers for git operations."""
from dataclasses import dataclass
from pathlib import Path

import git

from mbed_project.exceptions import VersionControlError
from mbed_project._internal.progress import ProgressReporter


@dataclass
class GitReference:
    """Git reference for a remote repository.

    Attributes:
        repo_url: URL of the git repository.
        ref: The reference commit sha, tag or branch.
    """

    repo_url: str
    ref: str


def clone(url: str, dst_dir: Path) -> git.Repo:
    """Clone a library repository.

    Args:
        git_ref: Object containing git information.
        dst_dir: Destination directory for the cloned repo.

    Raises:
        VersionControlError: Cloning the repository failed.
    """
    try:
        return git.Repo.clone_from(url, str(dst_dir), progress=ProgressReporter(name=url))
    except git.exc.GitCommandError as err:
        raise VersionControlError(f"Cloning git repository from url '{url}' failed. Error from VCS: {err.stderr}")


def checkout(repo: git.Repo, ref: str) -> None:
    """Check out the at specific reference in the given repository.

    Args:
        repo: git.Repo object where the checkout will be performed.
        ref: Git commit hash, branch or tag reference.

    Raises:
        VersionControlError: Check out failed.
    """
    git_object = git.repo.fun.name_to_object(repo, ref)
    commit = git.repo.fun.to_commit(git_object)
    try:
        repo.git.checkout(str(commit))
    except git.exc.GitCommandError as err:
        raise VersionControlError(f"Failed to check out revision '{commit}'. Error from VCS: {err.stderr}")


def init(path: Path) -> git.Repo:
    """Initialise a git repository at the given path.

    Args:
        path: Path where the repo will be initialised.

    Returns:
        Initialised git.Repo object.

    Raises:
        VersionControlError: initalising the repository failed.
    """
    try:
        return git.Repo.init(str(path))
    except git.exc.GitCommandError as err:
        raise VersionControlError(f"Failed to initialise git repository at path '{path}'. Error from VCS: {err.stderr}")
