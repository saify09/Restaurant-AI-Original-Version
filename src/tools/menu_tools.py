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

    def forward(self, item_name: str) -> str:
        results = self.rag_pipeline.query(f"Price and description for {item_name}")
        if not results:
            return f"Item '{item_name}' not found in menu."
        
        content = results[0]['content']
        # If the content is a markdown table row, try to make it even more explicit
        return f"Menu Retrieval Result: {content}\n\nPlease provide the specific price and description found in this text to the user or caller."
