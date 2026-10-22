"""Release targets shared by the build and archive helpers."""

from dataclasses import dataclass

EXPORT_MODES = ("template.debug", "template.release", "debug", "release")


@dataclass(frozen=True)
class ReleaseTarget:
    platform: str
    library: str
    editor: bool = True

    def filename(self, stem):
        return self.library.format(stem=stem)

    def library_entries(self, stem):
        os_name, separator, features = self.platform.partition(".")
        suffix = separator + features
        modes = ("editor", *EXPORT_MODES) if self.editor else EXPORT_MODES

        return {
            f"{os_name}.{mode}{suffix}": (
                f"bin/{'editor' if mode == 'editor' else 'runtime/release'}/"
                f"{self.filename(stem)}"
            )
            for mode in modes
        }


RELEASE_TARGETS = {
    "x86_64-unknown-linux-gnu": ReleaseTarget("linux.x86_64", "lib{stem}.so"),
    "aarch64-unknown-linux-gnu": ReleaseTarget("linux.arm64", "lib{stem}.so"),
    "i686-unknown-linux-gnu": ReleaseTarget("linux.x86_32", "lib{stem}.so"),
    "armv7-unknown-linux-gnueabihf": ReleaseTarget(
        "linux.arm32",
        "lib{stem}.so",
    ),
    "x86_64-pc-windows-msvc": ReleaseTarget("windows.x86_64", "{stem}.dll"),
    "aarch64-pc-windows-msvc": ReleaseTarget("windows.arm64", "{stem}.dll"),
    "i686-pc-windows-msvc": ReleaseTarget("windows.x86_32", "{stem}.dll"),
    "x86_64-apple-darwin": ReleaseTarget("macos.x86_64", "lib{stem}.dylib"),
    "aarch64-apple-darwin": ReleaseTarget("macos.arm64", "lib{stem}.dylib"),
    "aarch64-linux-android": ReleaseTarget(
        "android.arm64",
        "lib{stem}.so",
        editor=False,
    ),
    "armv7-linux-androideabi": ReleaseTarget(
        "android.arm32",
        "lib{stem}.so",
        editor=False,
    ),
    "x86_64-linux-android": ReleaseTarget(
        "android.x86_64",
        "lib{stem}.so",
        editor=False,
    ),
    "i686-linux-android": ReleaseTarget(
        "android.x86_32",
        "lib{stem}.so",
        editor=False,
    ),
    "ios-universal": ReleaseTarget(
        "ios",
        "{stem}.xcframework",
        editor=False,
    ),
    "wasm32-unknown-emscripten-threads": ReleaseTarget(
        "web.threads.wasm32",
        "{stem}.threads.wasm",
        editor=False,
    ),
    "wasm32-unknown-emscripten": ReleaseTarget(
        "web.wasm32",
        "{stem}.wasm",
        editor=False,
    ),
}


def release_target(target):
    # Local MinGW builds share the Windows descriptor without joining releases.
    if target == "x86_64-pc-windows-gnu":
        target = "x86_64-pc-windows-msvc"

    try:
        return RELEASE_TARGETS[target]
    except KeyError:
        raise ValueError(f"Unsupported release target {target!r}") from None
