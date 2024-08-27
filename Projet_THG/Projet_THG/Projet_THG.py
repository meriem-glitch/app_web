import tkinter as tk
import heapq

class Graph:
    def __init__(self):
        self.vertices = set()
        self.edges = []

    def add_edge(self, u, v, weight):
        self.vertices.add(u)
        self.vertices.add(v)
        self.edges.append((u, v, weight))

    def get_neighbors(self, vertex):
        neighbors = []
        for edge in self.edges:
            if edge[0] == vertex:
                neighbors.append((edge[1], edge[2]))
            elif edge[1] == vertex:
                neighbors.append((edge[0], edge[2]))
        return neighbors

    def bellman_ford(self, start):
        distance = {vertex: float('inf') for vertex in self.vertices}
        distance[start] = 0
        for _ in range(len(self.vertices) - 1):
            for u, v, w in self.edges:
                if distance[u] + w < distance[v]:
                    distance[v] = distance[u] + w
        return distance

    def dijkstra(self, start):
        distance = {vertex: float('inf') for vertex in self.vertices}
        distance[start] = 0
        priority_queue = [(0, start)]
        predecessors = {vertex: None for vertex in self.vertices}

        while priority_queue:
            dist_u, u = heapq.heappop(priority_queue)
            if dist_u > distance[u]:
                continue
            for v, w in self.get_neighbors(u):
                if dist_u + w < distance[v]:
                    distance[v] = dist_u + w
                    predecessors[v] = u
                    heapq.heappush(priority_queue, (distance[v], v))

        return distance, predecessors

    def welch_powell_stable_set(self):
        sorted_vertices = sorted(self.vertices, key=lambda vertex: len(self.get_neighbors(vertex)), reverse=True)
        stable_set = set()
        for vertex in sorted_vertices:
            if all(neighbor not in stable_set for neighbor, _ in self.get_neighbors(vertex)):
                stable_set.add(vertex)
        return stable_set

def kruskal(graph):
    def find(disjoint_set, vertex):
        if disjoint_set[vertex] != vertex:
            disjoint_set[vertex] = find(disjoint_set, disjoint_set[vertex])
        return disjoint_set[vertex]

    def union(disjoint_set, root_u, root_v):
        disjoint_set[root_u] = root_v

    minimum_spanning_tree = []
    disjoint_set = {vertex: vertex for vertex in graph.vertices}
    edges_sorted_by_weight = sorted(graph.edges, key=lambda x: x[2])

    for edge in edges_sorted_by_weight:
        u, v, weight = edge
        root_u = find(disjoint_set, u)
        root_v = find(disjoint_set, v)
        if root_u != root_v:
            minimum_spanning_tree.append((u, v, weight))
            union(disjoint_set, root_u, root_v)

    return minimum_spanning_tree

def max_spanning_tree(graph):
    def find(disjoint_set, vertex):
        if disjoint_set[vertex] != vertex:
            disjoint_set[vertex] = find(disjoint_set, disjoint_set[vertex])
        return disjoint_set[vertex]

    def union(disjoint_set, root_u, root_v):
        disjoint_set[root_u] = root_v

    maximum_spanning_tree = []
    disjoint_set = {vertex: vertex for vertex in graph.vertices}
    edges_sorted_by_weight = sorted(graph.edges, key=lambda x: x[2], reverse=True)

    for edge in edges_sorted_by_weight:
        u, v, weight = edge
        root_u = find(disjoint_set, u)
        root_v = find(disjoint_set, v)
        if root_u != root_v:
            maximum_spanning_tree.append((u, v, weight))
            union(disjoint_set, root_u, root_v)

    return maximum_spanning_tree

def prim(graph):
    minimum_spanning_tree = []
    visited = set()
    min_heap = []
    start_vertex = next(iter(graph.vertices))
    visited.add(start_vertex)

    for neighbor, weight in graph.get_neighbors(start_vertex):
        heapq.heappush(min_heap, (weight, start_vertex, neighbor))

    while min_heap:
        weight, u, v = heapq.heappop(min_heap)
        if v not in visited:
            visited.add(v)
            minimum_spanning_tree.append((u, v, weight))
            for neighbor, weight in graph.get_neighbors(v):
                if neighbor not in visited:
                    heapq.heappush(min_heap, (weight, v, neighbor))

    return minimum_spanning_tree

class GraphApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Graph Application")

        self.canvas = tk.Canvas(self.master, width=600, height=400, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.nodes = {}
        self.edges = set()
        self.node_counter = 0

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.draw_temp_line)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.selected_node = None
        self.temp_line = None
        self.drawing_edge = False

        self.finish_button = tk.Button(self.master, text="Terminer", command=self.compute_spanning_trees)
        self.finish_button.pack()

        self.shortest_path_button = tk.Button(self.master, text="Plus Court Chemin", command=self.compute_shortest_paths_wrapper)
        self.shortest_path_button.pack()

        self.stable_set_button = tk.Button(self.master, text="Ensemble Stable", command=self.compute_stable_set)
        self.stable_set_button.pack()

        self.back_button = tk.Button(self.master, text="Retour", command=self.undo_last_action)
        self.back_button.pack()

        self.clear_button = tk.Button(self.master, text="Effacer", command=self.clear_all)
        self.clear_button.pack()

        self.result_frame = tk.Frame(self.master)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(self.result_frame, height=10)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.result_text.tag_configure("readonly", foreground="black")
        self.result_text.bind("<Key>", lambda e: "break")

        self.scrollbar = tk.Scrollbar(self.result_frame, command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=self.scrollbar.set)

        self.actions = []

    def on_click(self, event):
        x, y = event.x, event.y
        clicked_node = self.get_node_at(x, y)
        if clicked_node:
            self.selected_node = clicked_node
            self.drawing_edge = True
        else:
            self.node_counter += 1
            node_text = f"{self.node_counter}"
            node = self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="white", outline="black")
            text = self.canvas.create_text(x, y, text=node_text)
            self.nodes[node] = (x, y, text)
           
            self.selected_node = node
            self.actions.append(('node', node))

    def draw_temp_line(self, event):
        if self.drawing_edge and self.selected_node is not None:
            if self.temp_line:
                self.canvas.delete(self.temp_line)
            start = self.nodes[self.selected_node]
            self.temp_line = self.canvas.create_line(start[0], start[1], event.x, event.y, fill="gray")

    def on_release(self, event):
        if self.drawing_edge and self.selected_node is not None:
            target_node = self.get_node_at(event.x, event.y)
            if target_node:
                start = self.nodes[self.selected_node]
                end = self.nodes[target_node]
                if target_node == self.selected_node:
                    line = self.canvas.create_oval(start[0] - 15, start[1] - 15, start[0] + 15, start[1] + 15, outline="black")
                else:
                    line = self.canvas.create_line(start[0], start[1], end[0], end[1], fill="black")
                self.edges.add((self.selected_node, target_node, line))
                self.actions.append(('edge', (self.selected_node, target_node, line)))
            if self.temp_line:
                self.canvas.delete(self.temp_line)
            self.selected_node = None
            self.drawing_edge = False

    def get_node_at(self, x, y):
        for node_id, (nx, ny, _) in self.nodes.items():
            if (nx-10 <= x <= nx+10) and (ny-10 <= y <= ny+10):
                return node_id
        return None

    def compute_spanning_trees(self):
        graph = self.get_graph()

        mst_kruskal = kruskal(graph)
        mst_prim = prim(graph)
        max_st = max_spanning_tree(graph)

        self.highlight_edges(mst_kruskal, color="blue")
        self.highlight_edges(mst_prim, color="green")
        self.highlight_edges(max_st, color="orange")

        results = ["\nMinimum Spanning Tree (Kruskal):"] + [str(edge) for edge in mst_kruskal]
        results += ["\nMinimum Spanning Tree (Prim):"] + [str(edge) for edge in mst_prim]
        results += ["\nMaximum Spanning Tree:"] + [str(edge) for edge in max_st]

        self.display_results(results)

    def compute_shortest_paths_wrapper(self):
        # Vous devez implémenter la fonction compute_shortest_paths avec les arguments appropriés
        # Comme indiqué dans le bouton Plus Court Chemin
        pass

    def compute_stable_set(self):
        graph = self.get_graph()
        stable_set = graph.welch_powell_stable_set()
        results = ["Ensemble stable (Stable Set) :"] + [f"{vertex}" for vertex in stable_set]
        self.highlight_stable_set(stable_set)
        self.display_results(results)

    def display_results(self, results):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        for result in results:
            self.result_text.insert(tk.END, str(result) + "\n")
        self.result_text.config(state=tk.DISABLED)

    def get_graph(self):
        graph = Graph()
        for edge in self.edges:
            start_node, end_node, _ = edge
            x1, y1, _ = self.nodes[start_node]
            x2, y2, _ = self.nodes[end_node]
            weight = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            graph.add_edge(start_node, end_node, weight)
        return graph

    def highlight_edges(self, edges, color):
        for u, v, _ in edges:
            for edge in self.edges:
                if (edge[0] == u and edge[1] == v) or (edge[0] == v and edge[1] == u):
                    self.canvas.itemconfig(edge[2], fill=color)

    def highlight_path(self, path, color):
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            for edge in self.edges:
                if (edge[0] == u and edge[1] == v) or (edge[0] == v and edge[1] == u):
                    self.canvas.itemconfig(edge[2], fill=color)

    def highlight_stable_set(self, stable_set):
        for node in stable_set:
            x, y, _ = self.nodes[node]
            self.canvas.itemconfig(node, fill="purple")
            self.canvas.itemconfig(self.nodes[node][2], fill="white")

    def undo_last_action(self):
        if self.actions:
            action, item = self.actions.pop()
            if action == 'node':
                node = item
                self.canvas.delete(node)
                del self.nodes[node]
                self.edges = {edge for edge in self.edges if edge[0] != node and edge[1] != node}
            elif action == 'edge':
                start_node, end_node, line = item
                self.canvas.delete(line)
                self.edges.remove(item)

    def clear_all(self):
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()
        self.actions.clear()
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
