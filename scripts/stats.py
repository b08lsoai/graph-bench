import dataset


def is_number(n):
    try:
        float(n)
        return True
    except ValueError:
        return False


def pretty_size(size):
    if size < 1000:
        return f"{size:.1f}"
    elif size < 1000 * 1000:
        return f"{(size / 1000.0):.1f}K"
    else:
        return f"{(size / 1000000.0):.1f}M"


def print_table(table):
    for row in table:
        print(", ".join([str(v) for v in row]))


def print_table_file(table, file):
    for row in table:
        file.write(", ".join([str(v) for v in row]) + "\n")

def build_table(cols: dict, prop, extra_prop=None):
    header = ["graph"]
    rows = dict()

    for col in cols.values():
        for row_name in col.keys():
            if row_name not in rows:
                rows[row_name] = []

    for name, col in cols.items():
        has_extra = False
        if extra_prop:
            # Берем первый результат из col и проверяем наличие атрибута
            first_result = next(iter(col.values())) if col else None
            if first_result and hasattr(first_result, extra_prop):
                has_extra = True
        
        if has_extra:
            header.append(f"{name} ({extra_prop})")
        else:
            header.append(name)
        for row_name in rows:
            if row_name in col:
                if has_extra:
                    # Если есть дополнительное свойство (вес)
                    extra_value = getattr(col[row_name], extra_prop, None)
                    if extra_value is not None:
                        rows[row_name].append(f"{extra_value:.2f}")
                    else:
                        rows[row_name].append(prop(col[row_name]))
                else:
                    rows[row_name].append(prop(col[row_name]))
            else:
                rows[row_name].append("none")

    return [header] + [[row_name] + row_data for row_name, row_data in rows.items()]


def output_stats(run_stats: dict):
    for algo, stats in run_stats.items():
        print("-" * 40 + f" {algo} " + "-" * 40)
        if algo == 'mst':
            # Сначала таблица времени
            print("\n[Time (ms)]")
            print_table(build_table(stats, lambda x: f"{x.avg():.2f}"))
            
            # Потом таблица весов
            print("\n[MST Weight]")
            print_table(build_table(stats, lambda x: x.avg(), extra_prop='mst_weight'))
        else:
            print_table(build_table(stats, lambda x: f"{x.avg():.2f}"))


def output_stats_overall(run_stats: dict, file_to_save):
    with open(file_to_save, 'w') as file:
        for algo, stats in run_stats.items():
            file.write(f"\n{algo.upper()}\n")

            if algo == 'mst':
                file.write("Time (ms):\n")
                print_table_file(build_table(stats, lambda x: f"{x.avg():.2f}"), file)
                file.write("\nMST Weight:\n")
                print_table_file(build_table(stats, lambda x: x.avg(), extra_prop='mst_weight'), file)
            else:
                print_table_file(build_table(stats, lambda x: f"{x.avg():.2f}"), file)


def output_stats_tool(run_stats: dict, file_to_save):
    with open(file_to_save, 'w') as file:
        file.write("graph,avg,sd,min,max,mst_weight\n")
        for algo, stats_algo in run_stats.items():
            file.write(f"{algo},,,,,\n")
            for tool, stats_tool in stats_algo.items():
                file.write(f"{tool},,,,,\n")
                for g, run in stats_tool.items():
                    mst_weight = getattr(run, 'mst_weight', None)
                    weight_str = f"{mst_weight:.2f}" if mst_weight is not None else ""
                    file.write(f"{g},{run.avg():.2f},{run.sd():.2f},{run.minimum():.2f},{run.maximum():.2f},{weight_str}\n")


def output_stats_graphs(file_to_save):
    with open(file_to_save, 'w') as file:
        file.write(f"|Name|Vertices|Edges|Avg Deg|Sd Deg|Min Deg|Max Deg|Link|\n")
        file.write(f"|:---|-------:|----:|------:|-----:|------:|------:|---:|\n")
        for name, graph in dataset.GRAPHS_DATA.items():
            file.write(f"|"
                       f"{name}|"
                       f"{pretty_size(graph.dim[0])}|"
                       f"{pretty_size(graph.size)}|"
                       f"{graph.deg_avg:.1f}|"
                       f"{graph.deg_sd:.1f}|"
                       f"{graph.deg_min:.1f}|"
                       f"{graph.deg_max:.1f}|"
                       f"[link]({graph.link})|\n")
