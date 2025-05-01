from inventory.models.category import Category

def test_category_creation():
    category = Category(
        category_id=1,
        name="Electrónicos",
        description="Dispositivos electrónicos"
    )
    
    assert category.name == "Electrónicos"
    assert category.category_id == 1