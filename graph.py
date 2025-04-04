import networkx as nx

def build_graph_with_external_nodes(page_data_dict):

        G = nx.DiGraph()
        internal_urls = set(page_data_dict.keys())

        print(f"Adding {len(internal_urls)} internal nodes...")
        for page_url, data in page_data_dict.items():
            attributes = {
                'description': data.get('description', ''),
                'texte': data.get('texte', ''),
                'embedding': data.get('embedding', None),
                'is_internal': True,
            }
            G.add_node(page_url, **attributes)

        print("Processing edges and adding external nodes...")
        external_nodes_added = set()
        for source_url, data in page_data_dict.items():
            if source_url not in internal_urls:
                continue

            outgoing_links = data.get('liens', [])
            for target_url in outgoing_links:
                if not target_url: 
                     continue

                if not G.has_node(target_url):
                    external_attributes = {
                       'description': '', 
                       'texte': '',
                       'is_internal': False, 
                    }
                    G.add_node(target_url, **external_attributes)
                    external_nodes_added.add(target_url)

                if source_url != target_url:
                    G.add_edge(source_url, target_url)

        print(f"Added {len(external_nodes_added)} external nodes.")
        print(f"Graph built successfully: {G.number_of_nodes()} total nodes, {G.number_of_edges()} edges.")

        return G