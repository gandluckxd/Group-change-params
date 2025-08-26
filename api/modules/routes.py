"""
API routes for Group Change Params
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from modules.models import (
    BreedChangeRequest, ColorChangeRequest, BreedOption, 
    ColorGroup, Color, OrderColor, APIResponse
)
from db.db_functions import (
    get_available_breeds, get_color_groups, get_colors_by_group,
    get_order_colors, get_order_info, update_breed_in_order, update_color_in_order,
    update_breed_in_stuffsets_orderitems, get_stuffsets_breeds_in_order, get_adds_breeds_in_order,
    get_stuffsets_colors_in_order, update_color_in_stuffsets_orderitems,
    test_connection
)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    db_ok = test_connection()
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "service": "Group Change Params API"
    }


@router.get("/breeds", response_model=List[BreedOption])
async def get_breeds():
    """Get all available breed options"""
    try:
        breeds_data = get_available_breeds()
        return [
            BreedOption(id=breed["ID"], code=breed["CODE"], type_id=breed["TYPEID"])
            for breed in breeds_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get breeds: {str(e)}")


@router.get("/color-groups", response_model=List[ColorGroup])
async def get_color_groups_endpoint():
    """Get all color groups"""
    try:
        groups_data = get_color_groups()
        return [ColorGroup(title=group["CG_TITLE"]) for group in groups_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get color groups: {str(e)}")


@router.get("/colors/{group_title}", response_model=List[Color])
async def get_colors_by_group_endpoint(group_title: str):
    """Get colors by group"""
    print(f"🔄 API: Запрос цветов для группы '{group_title}'")
    try:
        colors_data = get_colors_by_group(group_title)
        print(f"🔄 API: Получено {len(colors_data)} цветов из БД для группы '{group_title}'")
        
        result = [
            Color(
                color_id=i,  # Use index as ID since we only get title
                title=color["COLOR"],
                group_title=group_title  # Pass the actual group_title parameter
            )
            for i, color in enumerate(colors_data)
        ]
        
        print(f"🔄 API: Возвращаем {len(result)} цветов для группы '{group_title}'")
        return result
        
    except Exception as e:
        print(f"❌ API: Ошибка получения цветов для группы '{group_title}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get colors: {str(e)}")


@router.get("/orders/{order_id}/colors", response_model=List[OrderColor])
async def get_order_colors_endpoint(order_id: int):
    """Get colors used in specific order"""
    try:
        colors_data = get_order_colors(order_id)
        return [
            OrderColor(title=color["COLOR_TITLE"], count=1)  # Count not provided in new query
            for color in colors_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get order colors: {str(e)}")


@router.get("/orders/{order_id}/info")
async def get_order_info_endpoint(order_id: int):
    """Get order information"""
    try:
        order_data = get_order_info(order_id)
        if order_data and len(order_data) > 0:
            return order_data[0]  # Return first (should be only) record
        else:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    except Exception as e:
        print(f"Error in get_order_info_endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get order info: {str(e)}")


@router.post("/change-breed", response_model=APIResponse)
async def change_breed(request: BreedChangeRequest):
    """Change breed (wood type) in order"""
    print("🚀" + "=" * 79)
    print("🚀 API ENDPOINT: /change-breed CALLED")
    print(f"🚀 Request received: order_id={request.order_id}, breed_code='{request.breed_code}'")
    print("🚀" + "=" * 79)
    
    try:
        print("🚀 Calling update_breed_in_order function...")
        success = update_breed_in_order(request.order_id, request.breed_code, request.selected_breeds)
        
        print(f"🚀 update_breed_in_order returned: {success}")
        
        if success:
            response = APIResponse(
                success=True,
                message=f"Breed changed to '{request.breed_code}' in order {request.order_id}"
            )
            print(f"🚀 Returning SUCCESS response: {response}")
            print("🚀" + "=" * 79)
            return response
        else:
            response = APIResponse(
                success=False,
                message="Failed to update breed",
                error="Database update operation failed"
            )
            print(f"🚀 Returning FAILURE response: {response}")
            print("🚀" + "=" * 79)
            return response
    except Exception as e:
        print(f"🚀 EXCEPTION in change_breed endpoint: {e}")
        print("🚀" + "=" * 79)
        raise HTTPException(status_code=500, detail=f"Failed to change breed: {str(e)}")


@router.post("/change-color", response_model=APIResponse)
async def change_color(request: ColorChangeRequest):
    """Change color in order"""
    try:
        success = update_color_in_order(
            request.order_id, 
            request.new_color, 
            request.new_colorgroup, 
            request.old_colors
        )
        if success:
            return APIResponse(
                success=True,
                message=f"Color changed to '{request.new_color}' ({request.new_colorgroup}) in order {request.order_id}"
            )
        else:
            return APIResponse(
                success=False,
                message="Failed to update color",
                error="Database update operation failed"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change color: {str(e)}")


@router.get("/orders/{order_id}/stuffsets-breeds")
async def get_stuffsets_breeds_endpoint(order_id: int):
    """Get breeds used in stuffsets orderitems"""
    try:
        breeds_data = get_stuffsets_breeds_in_order(order_id)
        return [breed["BREED_CODE"] for breed in breeds_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stuffsets breeds: {str(e)}")


@router.get("/orders/{order_id}/adds-breeds")
async def get_adds_breeds_endpoint(order_id: int):
    """Get breeds used in adds (dополнения)"""
    try:
        breeds_data = get_adds_breeds_in_order(order_id)
        return [breed["BREED_CODE"] for breed in breeds_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get adds breeds: {str(e)}")


@router.get("/orders/{order_id}/stuffsets-colors")
async def get_stuffsets_colors_endpoint(order_id: int):
    """Get colors used in stuffsets orderitems"""
    try:
        colors_data = get_stuffsets_colors_in_order(order_id)
        return [{"title": color["COLOR_TITLE"]} for color in colors_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stuffsets colors: {str(e)}")


@router.post("/change-stuffsets-breed", response_model=APIResponse)
async def change_stuffsets_breed(request: BreedChangeRequest):
    """Change breed (wood type) in stuffsets orderitems"""
    print("🚀" + "=" * 79)
    print("🚀 API ENDPOINT: /change-stuffsets-breed CALLED")
    print(f"🚀 Request received: order_id={request.order_id}, breed_code='{request.breed_code}'")
    print("🚀" + "=" * 79)
    
    try:
        print("🚀 Calling update_breed_in_stuffsets_orderitems function...")
        success = update_breed_in_stuffsets_orderitems(request.order_id, request.breed_code, request.selected_breeds)
        
        print(f"🚀 update_breed_in_stuffsets_orderitems returned: {success}")
        
        if success:
            response = APIResponse(
                success=True,
                message=f"Stuffsets breed changed to '{request.breed_code}' in order {request.order_id}"
            )
            print(f"🚀 Returning SUCCESS response: {response}")
            print("🚀" + "=" * 79)
            return response
        else:
            response = APIResponse(
                success=False,
                message="Failed to update stuffsets breed",
                error="Database update operation failed"
            )
            print(f"🚀 Returning FAILURE response: {response}")
            print("🚀" + "=" * 79)
            return response
    except Exception as e:
        print(f"🚀 EXCEPTION in change_stuffsets_breed endpoint: {e}")
        print("🚀" + "=" * 79)
        raise HTTPException(status_code=500, detail=f"Failed to change stuffsets breed: {str(e)}")


@router.post("/change-stuffsets-color", response_model=APIResponse)
async def change_stuffsets_color(request: ColorChangeRequest):
    """Change color in stuffsets orderitems"""
    print("🚀" + "=" * 79)
    print("🚀 API ENDPOINT: /change-stuffsets-color CALLED")
    print(f"🚀 Request received: order_id={request.order_id}, new_color='{request.new_color}', old_colors={request.old_colors}")
    print("🚀" + "=" * 79)
    
    try:
        print("🚀 Calling update_color_in_stuffsets_orderitems function...")
        success = update_color_in_stuffsets_orderitems(
            request.order_id, 
            request.new_color, 
            request.new_colorgroup, 
            request.old_colors
        )
        
        print(f"🚀 update_color_in_stuffsets_orderitems returned: {success}")
        
        if success:
            response = APIResponse(
                success=True,
                message=f"Stuffsets colors changed to '{request.new_color}' in order {request.order_id}"
            )
            print(f"🚀 Returning SUCCESS response: {response}")
            print("🚀" + "=" * 79)
            return response
        else:
            response = APIResponse(
                success=False,
                message="Failed to update stuffsets colors",
                error="Database update operation failed"
            )
            print(f"🚀 Returning FAILURE response: {response}")
            print("🚀" + "=" * 79)
            return response
    except Exception as e:
        print(f"🚀 EXCEPTION in change_stuffsets_color endpoint: {e}")
        print("🚀" + "=" * 79)
        raise HTTPException(status_code=500, detail=f"Failed to change stuffsets color: {str(e)}")
