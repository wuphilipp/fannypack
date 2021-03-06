import argparse
import glob
import os

from ._buddy_cli_subcommand import Subcommand


class RenameSubcommand(Subcommand):
    """Rename a Buddy experiment.
    """

    subcommand: str = "rename"

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "source",
            type=str,
            help="Current name of experiment, as printed by `$ buddy list`.",
        )
        parser.add_argument("dest", type=str, help="New name of experiment.")

    @classmethod
    def main(cls, args: argparse.Namespace) -> None:
        # Get old, new experiment names
        old_experiment_name = args.source
        new_experiment_name = args.dest

        # Validate that new experiment name doesn't exist
        new_checkpoint_files = glob.glob(
            os.path.join(
                args.checkpoint_dir, f"{glob.escape(new_experiment_name)}-*.ckpt"
            )
        )
        if len(new_checkpoint_files) != 0:
            raise RuntimeError(
                f"Checkpoints already exist for destination name: {new_experiment_name}"
            )
        if os.path.exists(os.path.join(args.log_dir, f"{new_experiment_name}")):
            raise RuntimeError(
                f"Logs already exist for destination name: {new_experiment_name}"
            )
        if os.path.exists(
            os.path.join(args.metadata_dir, f"{new_experiment_name}.yaml")
        ):
            raise RuntimeError(
                f"Metadata already exist for destination name: {new_experiment_name}"
            )

        # Move checkpoint files
        checkpoint_paths = glob.glob(
            os.path.join(
                args.checkpoint_dir, f"{glob.escape(old_experiment_name)}-*.ckpt"
            )
        )
        print(f"Found {len(checkpoint_paths)} checkpoint files")
        for path in checkpoint_paths:
            # Get new checkpoint path
            prefix = os.path.join(args.checkpoint_dir, f"{old_experiment_name}-")
            suffix = ".ckpt"
            assert path.startswith(prefix)
            assert path.endswith(suffix)
            label = path[len(prefix) : -len(suffix)]
            new_path = os.path.join(
                args.checkpoint_dir, f"{new_experiment_name}-{label}.ckpt"
            )

            # Move checkpoint
            print(f"> Moving {path} to {new_path}")
            os.rename(path, new_path)

        # Move metadata
        metadata_path = os.path.join(args.metadata_dir, f"{old_experiment_name}.yaml")
        if os.path.exists(metadata_path):
            new_path = os.path.join(args.metadata_dir, f"{new_experiment_name}.yaml")
            print(f"Moving {metadata_path} to {new_path}")
            os.rename(metadata_path, new_path)
        else:
            print("No metadata found")

        # Move logs
        metadata_path = os.path.join(args.log_dir, f"{old_experiment_name}")
        if os.path.exists(metadata_path):
            new_path = os.path.join(args.log_dir, f"{new_experiment_name}")
            print(f"Moving {metadata_path} to {new_path}")
            os.rename(metadata_path, new_path)
        else:
            print("No logs found")
