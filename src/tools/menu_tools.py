from smolagents import Tool
from src.utils.rag_pipeline import RAGPipeline

class MenuLookupTool(Tool):
    name = "menu_lookup"
    description = "Retrieves pricing and availability details for menu items. Use this to find prices before creating an order."
    inputs = {
        "item_name": {"type": "string", "description": "Name of the food or drink item"}
    }
    output_type = "string"

    def __init__(self, rag_pipeline: RAGPipeline, **kwargs):
        super().__init__(**kwargs)
        self.rag_pipeline = rag_pipeline

    def forward(self, item_name: str = "all") -> str:
        if item_name.lower() in ["all", "menu", "entire menu", ""]:
            results = self.rag_pipeline.query("restaurant menu table items prices")
        else:
            results = self.rag_pipeline.query(f"Price and description for {item_name}")
            
        if not results:
            return f"Item '{item_name}' not found in menu."
        
        # Join all results to ensure the agent sees the whole table
        context = "\n\n".join([res['content'] for res in results])
        return f"Menu Retrieval Result:\n{context}\n\nNote: Provide the relevant items and prices to the user."
