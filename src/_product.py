from dataclasses import dataclass

@dataclass
class Product:
    """
    Convenience class that acts as a container for products attributes,
    and as a helper for its representation.
    """
    href: str

    name: str = None
    price: float = None
    price_unit: str = None
    description: str = None
    rating: float = None
    page_size: int = None

    def as_dict(self):
        """Represents the product attributes as a dict"""
        return {
            'Title': self.name,
            'Price': self.price,
            'Price_Unit': self.price_unit,
            'Short_Desc': self.description,
            'Rating': self.rating,
            'Page_Size_KB': self.page_size
        }