import cloudinary
import cloudinary_services
from cloudinary.utils import cloudinary_url
from ..config.settings import settings as st


# Cloudinary Configuration
cloudinary.config(
    cloud_name = st.CLOUD_NAME,
    api_key = st.CLOUD_API_KEY,
    api_secret = st.CLOUD_SECRET_KEY,
    secure = True
)


"""
HOW TO USE:
"""

"""

"""