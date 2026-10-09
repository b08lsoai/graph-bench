import subprocess
import driver
import config
import dataset

__all__ = [
    "DriverGunrock"
]


class DriverGunrock(driver.Driver):

    def __init__(self):
        super().__init__()
        self.exec_dir = config.DEPS / "gunrock" / "build" / "bin"
        self.bfs = "bfs"
        self.sssp = "sssp"
        self.pr = "pr"
        self.tc = "tc"
        self.mst = "mst"

    def name(self) -> str:
        return "gunrock"

    def run_bfs(self, graph: dataset.Graph, source_vertex, num_iterations) -> driver.ExecutionResult:
        args = ["-m", str(graph.path_original()), "-s", str(source_vertex)]
        return DriverGunrock._run_many(self.exec_dir / self.bfs, args, num_iterations)

    def run_sssp(self, graph: dataset.Graph, source_vertex, num_iterations) -> driver.ExecutionResult:
        args = ["-m", str(graph.path_original()), "-s", str(source_vertex)]
        return DriverGunrock._run_many(self.exec_dir / self.sssp, args, num_iterations)

    def run_pr(self, graph: dataset.Graph, num_iterations) -> driver.ExecutionResult:
        args = ["-m", str(graph.path_original())]
        return DriverGunrock._run_many(self.exec_dir / self.pr, args, num_iterations)

    def run_tc(self, graph: dataset.Graph, num_iterations) -> driver.ExecutionResult:
        args = ["-m", str(graph.path_original())]
        return DriverGunrock._run_many(self.exec_dir / self.tc, args, num_iterations)

    def run_mst(self, graph: dataset.Graph, num_iterations) -> driver.ExecutionResult:
        args = ["-m", str(graph.path_original())]
        return DriverGunrock._run_many(self.exec_dir / self.mst, args, num_iterations,
                                       parse_weight=True)

    @staticmethod
    def _run_many(executable, args, num_iterations, parse_weight=False):
        """
        The examples print one "GPU Elapsed Time : X (ms)" line per run, so we
        invoke the binary once with `-n num_iterations` and treat the
        first measurement as a warm-up. This mirrors spla/lagraph, which also
        perform `num_iterations` runs in total (1 warm-up + num_iterations-1
        measured runs).
        """
        args = args + ["-n", str(num_iterations)]
        output = subprocess.check_output([str(executable)] + args)
        lines = output.decode("ASCII").replace("\r", "").split("\n")
        runs = []
        mst_weight = None
        for line in lines:
            if line.startswith("GPU Elapsed Time :"):
                runs.append(float(line.split(":")[1].split("(")[0].strip()))
            if parse_weight and line.startswith("GPU MST Weight:"):
                mst_weight = float(line.split(":")[1].strip())
        return driver.ExecutionResult(runs[0], runs[1:], mst_weight=mst_weight)
