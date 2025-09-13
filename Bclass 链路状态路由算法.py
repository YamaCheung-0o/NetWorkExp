import networkx as nx
import matplotlib.pyplot as plt
import random
import copy
from matplotlib.animation import FuncAnimation

# 生成随机网络拓扑
def generate_topology(num_nodes, connection_prob, seed=None):
    """生成随机网络拓扑图，节点间距离随机分配"""
    random.seed(seed)
    G = nx.erdos_renyi_graph(num_nodes, connection_prob)
    
    # 为每条边分配随机权重（距离）
    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(1, 10)
    
    return G

# 节点类：表示网络中的一个节点
class Node:
    def __init__(self, node_id, graph):
        self.node_id = node_id  # 节点ID
        self.graph = graph      # 完整拓扑图的引用
        self.neighbors = list(graph.neighbors(node_id))  # 邻居节点列表
        self.link_state = {}    # 链路状态表：{邻居节点: 距离}
        self.routing_table = {} # 路由表：{目标节点: (下一跳节点, 距离)}
        
        # 初始化链路状态表（仅包含直接连接的邻居）
        for neighbor in self.neighbors:
            self.link_state[neighbor] = graph[node_id][neighbor]['weight']
        
        # 初始化路由表（仅包含直接连接的邻居）
        for neighbor in self.neighbors:
            self.routing_table[neighbor] = (neighbor, self.link_state[neighbor])
    
    def build_network_topology(self, all_lsp):
        """根据所有节点的链路状态分组构建完整网络拓扑"""
        # 创建一个新图表示全局拓扑
        global_topology = nx.Graph()
        
        # 添加所有节点
        for node_id in all_lsp:
            global_topology.add_node(node_id)
        
        # 添加所有边（基于链路状态分组）
        for node_id, lsp in all_lsp.items():
            for neighbor, weight in lsp.items():
                if not global_topology.has_edge(node_id, neighbor):
                    global_topology.add_edge(node_id, neighbor, weight=weight)
        
        return global_topology
    
    def calculate_routing_table(self, global_topology):
        """使用Dijkstra算法计算最短路径并更新路由表"""
        # 计算从当前节点到所有其他节点的最短路径
        shortest_paths = nx.single_source_dijkstra_path(global_topology, self.node_id)
        shortest_distances = nx.single_source_dijkstra_path_length(global_topology, self.node_id)
        
        # 更新路由表
        self.routing_table = {}
        for target, path in shortest_paths.items():
            if len(path) >= 2:  # 至少有两个节点（当前节点和目标节点）
                next_hop = path[1]  # 路径中的第二个节点是下一跳
                distance = shortest_distances[target]
                self.routing_table[target] = (next_hop, distance)
    
    def get_routing_table(self):
        """返回路由表的格式化字符串"""
        table_str = f"节点 {self.node_id} 的路由表:\n"
        table_str += "目标节点\t下一跳节点\t距离\n"
        for target, (next_hop, distance) in sorted(self.routing_table.items()):
            table_str += f"{target}\t\t{next_hop}\t\t{distance}\n"
        return table_str

# 模拟链路状态路由过程
def simulate_link_state_routing(G):
    """模拟链路状态路由算法的执行过程"""
    # 创建节点对象列表
    nodes = {node_id: Node(node_id, G) for node_id in G.nodes()}
    
    # 步骤1：每个节点广播自己的链路状态分组(LSP)
    all_lsp = {node_id: node.link_state for node_id, node in nodes.items()}
    
    # 步骤2：每个节点根据收到的LSP构建完整拓扑并计算路由表
    for node_id, node in nodes.items():
        global_topology = node.build_network_topology(all_lsp)
        node.calculate_routing_table(global_topology)
    
    return nodes

# 可视化函数
def visualize_topology(G, pos=None, title="随机网络路由拓扑图", show_weights=True):
    """可视化网络拓扑图"""
    if pos is None:
        pos = nx.spring_layout(G)  # 使用spring布局算法排列节点
    
    plt.figure(figsize=(10, 8))
    plt.title(title)
    
    # 绘制节点
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
    
    # 绘制边
    nx.draw_networkx_edges(G, pos, width=2, edge_color='gray')
    
    # 绘制节点标签
    nx.draw_networkx_labels(G, pos, font_size=14, font_family='sans-serif')
    
    # 绘制边权重
    if show_weights:
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)
    
    plt.axis('off')
    plt.tight_layout()
    return pos

# 模拟拓扑变化
def simulate_topology_change(G, change_type='random'):
    """模拟网络拓扑的变化，如链路增加、删除或权重变化"""
    G = copy.deepcopy(G)  # 创建拓扑的副本，避免修改原始图
    
    if change_type == 'random':
        # 随机选择一种变化类型
        change_type = random.choice(['add_link', 'remove_link', 'change_weight'])
    
    if change_type == 'add_link':
        # 尝试添加一条新链路
        nodes = list(G.nodes())
        # 查找所有可能的边
        possible_edges = []
        for u in nodes:
            for v in nodes:
                if u < v and not G.has_edge(u, v):
                    possible_edges.append((u, v))
        
        if possible_edges:
            u, v = random.choice(possible_edges)
            weight = random.randint(1, 10)
            G.add_edge(u, v, weight=weight)
            print(f"添加链路: {u} <-> {v}，权重: {weight}")
        else:
            print("无法添加新链路：所有可能的链路已存在")
    
    elif change_type == 'remove_link':
        # 尝试删除一条现有链路
        if G.edges():
            u, v = random.choice(list(G.edges()))
            G.remove_edge(u, v)
            print(f"删除链路: {u} <-> {v}")
        else:
            print("无法删除链路：网络中没有链路")
    
    elif change_type == 'change_weight':
        # 尝试更改现有链路的权重
        if G.edges():
            u, v = random.choice(list(G.edges()))
            old_weight = G[u][v]['weight']
            new_weight = random.randint(1, 10)
            while new_weight == old_weight:  # 确保权重确实发生了变化
                new_weight = random.randint(1, 10)
            G[u][v]['weight'] = new_weight
            print(f"更改链路权重: {u} <-> {v}，从 {old_weight} 变为 {new_weight}")
        else:
            print("无法更改权重：网络中没有链路")
    
    return G


# 5. 主函数
def main():
    # 生成随机拓扑
    G = generate_topology(num_nodes=6, connection_prob=0.35, seed=42)
    
    # 可视化初始拓扑
    pos = visualize_topology(G, title="初始随机网络路由拓扑")
    plt.show()
    
    # 模拟链路状态路由算法
    nodes = simulate_link_state_routing(G)
    
    # 打印每个节点的路由表
    for node_id, node in nodes.items():
        print(node.get_routing_table())
        print("-" * 40)

    # 模拟拓扑变化
    G_updated = simulate_topology_change(G)
    
    # 可视化更新后的拓扑
    visualize_topology(G_updated, pos=pos, title="更新后的随机网络路由拓扑")
    plt.show()
    
    # 重新运行路由算法以更新路由表
    nodes = simulate_link_state_routing(G_updated)
    
    # 打印每个节点的更新后路由表
    print("更新后的路由表:")
    for node_id, node in nodes.items():
        print(node.get_routing_table())
        print("-" * 40)


if __name__ == "__main__":
    main()