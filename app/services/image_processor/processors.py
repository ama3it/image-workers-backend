import os
from PIL import Image
from io import BytesIO

def process_greyscale(storage_path, image_data):
    """
    Convert an image to greyscale
    
    Args:
        storage_path: Original path of the image
        image_data: Binary image data
        
    Returns:
        tuple: (processed_file_path, processed_image_data)
    """
    img = Image.open(BytesIO(image_data))
    
    # Convert to greyscale
    grey_img = img.convert('L')
    
    # Save to BytesIO
    output = BytesIO()
    save_format = get_save_format(storage_path)
    grey_img.save(output, format=save_format)
    output_data = output.getvalue()
    
    filename = os.path.basename(storage_path)
    name, ext = os.path.splitext(filename)
    processed_path = f"{name}_grey{ext}"
    
    return processed_path, output_data

def process_thumbnail(storage_path, image_data, size=(128, 128)):
    """
    Create a thumbnail of the image
    
    Args:
        storage_path: Original path of the image
        image_data: Binary image data
        size: Thumbnail size as (width, height)
        
    Returns:
        tuple: (processed_file_path, processed_image_data)
    """
    img = Image.open(BytesIO(image_data))
    
    # Create thumbnail
    img.thumbnail(size)
    
   
    output = BytesIO()
    save_format = get_save_format(storage_path)
    img.save(output, format=save_format)
    output_data = output.getvalue()
    
    filename = os.path.basename(storage_path)
    name, ext = os.path.splitext(filename)
    processed_path = f"{name}_thumb{ext}"
    
    return processed_path, output_data

def process_resize(storage_path, image_data, width, height):
    """
    Resize an image to specified dimensions
    
    Args:
        storage_path: Original path of the image
        image_data: Binary image data
        width: Target width
        height: Target height
        
    Returns:
        tuple: (processed_file_path, processed_image_data)
    """

    img = Image.open(BytesIO(image_data))
    
    # Resize image
    resized_img = img.resize((width, height), Image.LANCZOS)
    
    output = BytesIO()
    save_format = get_save_format(storage_path)
    resized_img.save(output, format=save_format)
    output_data = output.getvalue()
    
   
    filename = os.path.basename(storage_path)
    name, ext = os.path.splitext(filename)
    processed_path = f"{name}_resized_{width}x{height}{ext}"
    
    return processed_path, output_data

def get_save_format(file_path):
    """
    Determine the save format based on file extension
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.jpg' or ext == '.jpeg':
        return 'JPEG'
    elif ext == '.png':
        return 'PNG'
    elif ext == '.webp':
        return 'WEBP'
    else:
        # Default to JPEG if unknown
        return 'JPEG'