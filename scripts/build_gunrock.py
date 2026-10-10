import itertools
import os
import subprocess
import config
import argparse

GUNROCK_PATH = config.DEPS / "gunrock"
GUNROCK_BUILD = GUNROCK_PATH / "build"
GUNROCK_TARGETS = ["mst", "bfs", "sssp", "pr", "tc"]

# NOTE: The MST benchmark uses the upstream Gunrock examples with
# local-only patches applied to deps/gunrock (no fork). To make the
# examples print one "GPU Elapsed Time : X (ms)" line per run and
# (for MST) the total tree weight, the following changes must be
# applied locally before building:
#
#   examples/algorithms/mst/mst.cu
#     - add the `-n/--num_runs` option (default 1);
#     - run `gunrock::mst::run` `num_runs` times and print
#       "GPU Elapsed Time : <time> (ms)" after every run;
#     - print the resulting tree weight as "GPU MST Weight: <weight>"
#       (parsed from stdout by driver_gunrock.py) once after the runs.
#
#   examples/algorithms/{bfs,sssp,pr,tc}/*.cu
#     - print "GPU Elapsed Time : <time> (ms)" for every run, so
#       driver_gunrock.py can collect all measurements from a single
#       invocation (tc also gets the `-n/--num_runs` option).
#
# These patches are intentionally NOT committed (pushing a gitlink to a
# local submodule commit would break `git submodule update` for other
# machines).


def build(args):
    try:
        env = os.environ.copy()
        env["CC"] = args.cc
        env["CXX"] = args.cxx
        env["CUDAHOSTCXX"] = args.cudacxx
        print(f"Build gunrock inside {GUNROCK_PATH} directory")
        print(f"Using env: CC={args.cc} CXX={args.cxx} CUDAHOSTCXX={args.cudacxx}")

        cmake_arch = ["-DCMAKE_CUDA_ARCHITECTURES=native"] if args.autodetect \
            else [f"-DCMAKE_CUDA_ARCHITECTURES={args.gencode}"]

        subprocess.check_call(["cmake", str(GUNROCK_PATH), "-B", str(GUNROCK_BUILD),
                               "-DESSENTIALS_NVIDIA_BACKEND=ON",
                               "-DESSENTIALS_AMD_BACKEND=OFF",
                               "-DESSENTIALS_BUILD_EXAMPLES=ON",
                               "-DCMAKE_BUILD_TYPE=Release",
                               f"-DCMAKE_CXX_COMPILER={args.cxx}",
                               f"-DCMAKE_C_COMPILER={args.cc}",
                               f"-DCMAKE_CUDA_HOST_COMPILER={args.cudacxx}"] +
                              cmake_arch,
                              env=env)
        subprocess.check_call(["cmake", "--build", str(GUNROCK_BUILD)] +
                              list(itertools.chain(*[["-t", t] for t in GUNROCK_TARGETS])) +
                              ["-j", str(args.j)])
    except subprocess.CalledProcessError as error:
        print("Failed to build gunrock. Error:", error)
        return 1

    print("Done!")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--j", default=4, help="Number of threads used to build")
    parser.add_argument("--cc", default="/usr/bin/gcc-12", help="Path to CC compiler")
    parser.add_argument("--cxx", default="/usr/bin/g++-12", help="Path to CXX compiler")
    parser.add_argument("--cudacxx", default="/usr/bin/g++-12", help="Path to CUDAHOSTCXX compiler")
    parser.add_argument("--autodetect", default=True, help="Autodetect target architecture")
    parser.add_argument("--gencode", default="61", help="Target sm and compute architecture "
                                                        "(numeric part, e.g. 61, 80, 90)")
    args = parser.parse_args()
    return build(args)


if __name__ == '__main__':
    exit(main())
