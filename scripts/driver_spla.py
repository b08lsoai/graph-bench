import os
import pathlib
import subprocess
import driver
import config
import dataset

__all__ = [
    "DriverSpla"
]


class DriverSpla(driver.Driver):
    """
    SPLA library driver.

    Use `BENCH_DRIVER_SPLA` env variable to specify custom path to spla driver
    """

    def __init__(self):
        super().__init__()
        self.exec_dir = config.DEPS / "spla" / "build"
        self.spla_bfs = "bfs" + config.EXECUTABLE_EXT
        self.spla_sssp = "sssp" + config.EXECUTABLE_EXT
        self.spla_pr = "pr" + config.EXECUTABLE_EXT
        self.spla_tc = "tc" + config.EXECUTABLE_EXT
        self.spla_mst = "mst" + config.EXECUTABLE_EXT
        self.undirected = 0
        self.run_cpu = False

        try:
            self.exec_dir = pathlib.Path(os.environ["BENCH_DRIVER_SPLA"])
            print("Set spla exec dir to:", self.exec_dir)
        except KeyError:
            pass

    def name(self) -> str:
        return "spla"

    def run_bfs(self, graph: dataset.Graph, source_vertex, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.spla_bfs),
             f"--mtxpath={graph.path_original()}",
             f"--niters={num_iterations}",
             f"--source={source_vertex}",
             f"--run-cpu={self.run_cpu}",
             f"--undirected={self.undirected}",
             self._get_platform(),
             self._get_device()])
        return DriverSpla._parse_output(output)

    def run_sssp(self, graph: dataset.Graph, source_vertex, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.spla_sssp),
             f"--mtxpath={graph.path_original()}",
             f"--niters={num_iterations}",
             f"--source={source_vertex}",
             f"--run-cpu={self.run_cpu}",
             f"--undirected={self.undirected}",
             self._get_platform(),
             self._get_device()])
        return DriverSpla._parse_output(output)

    def run_pr(self, graph: dataset.Graph, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.spla_pr),
             f"--mtxpath={graph.path_original()}",
             f"--run-cpu={self.run_cpu}",
             f"--niters={num_iterations}",
             self._get_platform(),
             self._get_device()])
        return DriverSpla._parse_output(output)

    def run_tc(self, graph: dataset.Graph, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.spla_tc),
             f"--mtxpath={graph.path_original()}",
             f"--run-cpu={self.run_cpu}",
             f"--niters={num_iterations}",
             self._get_platform(),
             self._get_device()])
        return DriverSpla._parse_output(output)

    def run_mst(self, graph: dataset.Graph, num_iterations) -> driver.ExecutionResult:
        output = subprocess.check_output(
            [str(self.exec_dir / self.spla_mst),
             f"--mtxpath={graph.path_original()}",
             f"--run-cpu={self.run_cpu}",
             f"--niters={num_iterations}",
             self._get_platform(),
             self._get_device()])
        return DriverSpla._parse_output_mst(output)

    @staticmethod
    def _parse_output(output):
        lines = output.decode("utf-8").replace("\r", "").split("\n")
        runs = []
        for line in lines:
            if line.startswith("gpu(ms):"):
                runs = [float(v) for v in line.split(", ")[1:-1]]
        return driver.ExecutionResult(runs[0], runs[1:])

    @staticmethod
    def _parse_output_mst(output):
        
        """Парсинг для MST с извлечением веса"""
        text = output.decode("utf-8")
        lines = text.replace("\r", "").split("\n")
        
        runs = []
        mst_weight = None
        
        for line in lines:
            if "gpu(ms):" in line:
                # Убираем "gpu(ms):" и разделяем по запятым
                time_str = line.replace("gpu(ms):", "").strip()
                # Убираем последнюю запятую если есть
                if time_str.endswith(','):
                    time_str = time_str[:-1]
                # Разделяем по запятым
                parts = time_str.split(",")
                for part in parts:
                    part = part.strip()
                    if part:
                        try:
                            runs.append(float(part))
                        except ValueError:
                            pass
                break
        
        for line in lines:
            if "MST total weight:" in line:
                weight_str = line.split("MST total weight:")[-1].strip()
                try:
                    mst_weight = float(weight_str)
                except ValueError:
                    pass
                break
        
        # Защита от пустых данных
        if not runs:
            return driver.ExecutionResult(0, [], mst_weight=mst_weight)
        
        warm_up = runs[0]
        times = runs[1:] if len(runs) > 1 else []
        
        return driver.ExecutionResult(warm_up, times, mst_weight=mst_weight)

    def _get_platform(self):
        return f"--platform={self.params['platform']}"

    def _get_device(self):
        return f"--device={self.params['device']}"
