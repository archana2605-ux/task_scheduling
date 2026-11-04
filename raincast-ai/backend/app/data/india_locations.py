"""India locations database — major cities, states, and districts with coordinates."""

INDIA_CITIES = [
    # Format: {"name": str, "state": str, "district": str, "lat": float, "lon": float}
    {"name": "Mumbai", "state": "Maharashtra", "district": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Delhi", "state": "Delhi", "district": "New Delhi", "lat": 28.6139, "lon": 77.2090},
    {"name": "Bengaluru", "state": "Karnataka", "district": "Bangalore Urban", "lat": 12.9716, "lon": 77.5946},
    {"name": "Chennai", "state": "Tamil Nadu", "district": "Chennai", "lat": 13.0827, "lon": 80.2707},
    {"name": "Kolkata", "state": "West Bengal", "district": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    {"name": "Hyderabad", "state": "Telangana", "district": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    {"name": "Ahmedabad", "state": "Gujarat", "district": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
    {"name": "Pune", "state": "Maharashtra", "district": "Pune", "lat": 18.5204, "lon": 73.8567},
    {"name": "Jaipur", "state": "Rajasthan", "district": "Jaipur", "lat": 26.9124, "lon": 75.7873},
    {"name": "Surat", "state": "Gujarat", "district": "Surat", "lat": 21.1702, "lon": 72.8311},
    {"name": "Lucknow", "state": "Uttar Pradesh", "district": "Lucknow", "lat": 26.8467, "lon": 80.9462},
    {"name": "Kanpur", "state": "Uttar Pradesh", "district": "Kanpur Nagar", "lat": 26.4499, "lon": 80.3319},
    {"name": "Nagpur", "state": "Maharashtra", "district": "Nagpur", "lat": 21.1458, "lon": 79.0882},
    {"name": "Indore", "state": "Madhya Pradesh", "district": "Indore", "lat": 22.7196, "lon": 75.8577},
    {"name": "Thane", "state": "Maharashtra", "district": "Thane", "lat": 19.2183, "lon": 72.9781},
    {"name": "Bhopal", "state": "Madhya Pradesh", "district": "Bhopal", "lat": 23.2599, "lon": 77.4126},
    {"name": "Visakhapatnam", "state": "Andhra Pradesh", "district": "Visakhapatnam", "lat": 17.6868, "lon": 83.2185},
    {"name": "Patna", "state": "Bihar", "district": "Patna", "lat": 25.5941, "lon": 85.1376},
    {"name": "Vadodara", "state": "Gujarat", "district": "Vadodara", "lat": 22.3072, "lon": 73.1812},
    {"name": "Ghaziabad", "state": "Uttar Pradesh", "district": "Ghaziabad", "lat": 28.6692, "lon": 77.4538},
    {"name": "Ludhiana", "state": "Punjab", "district": "Ludhiana", "lat": 30.9010, "lon": 75.8573},
    {"name": "Agra", "state": "Uttar Pradesh", "district": "Agra", "lat": 27.1767, "lon": 78.0081},
    {"name": "Nashik", "state": "Maharashtra", "district": "Nashik", "lat": 19.9975, "lon": 73.7898},
    {"name": "Faridabad", "state": "Haryana", "district": "Faridabad", "lat": 28.4089, "lon": 77.3178},
    {"name": "Meerut", "state": "Uttar Pradesh", "district": "Meerut", "lat": 28.9845, "lon": 77.7064},
    {"name": "Rajkot", "state": "Gujarat", "district": "Rajkot", "lat": 22.3039, "lon": 70.8022},
    {"name": "Kalyan", "state": "Maharashtra", "district": "Thane", "lat": 19.2437, "lon": 73.1355},
    {"name": "Vasai-Virar", "state": "Maharashtra", "district": "Palghar", "lat": 19.4260, "lon": 72.8347},
    {"name": "Varanasi", "state": "Uttar Pradesh", "district": "Varanasi", "lat": 25.3176, "lon": 82.9739},
    {"name": "Srinagar", "state": "Jammu & Kashmir", "district": "Srinagar", "lat": 34.0836, "lon": 74.7973},
    {"name": "Aurangabad", "state": "Maharashtra", "district": "Aurangabad", "lat": 19.8762, "lon": 75.3433},
    {"name": "Dhanbad", "state": "Jharkhand", "district": "Dhanbad", "lat": 23.7957, "lon": 86.4304},
    {"name": "Amritsar", "state": "Punjab", "district": "Amritsar", "lat": 31.6340, "lon": 74.8723},
    {"name": "Raipur", "state": "Chhattisgarh", "district": "Raipur", "lat": 21.2514, "lon": 81.6296},
    {"name": "Allahabad (Prayagraj)", "state": "Uttar Pradesh", "district": "Prayagraj", "lat": 25.4358, "lon": 81.8463},
    {"name": "Coimbatore", "state": "Tamil Nadu", "district": "Coimbatore", "lat": 11.0168, "lon": 76.9558},
    {"name": "Jabalpur", "state": "Madhya Pradesh", "district": "Jabalpur", "lat": 23.1815, "lon": 79.9864},
    {"name": "Gwalior", "state": "Madhya Pradesh", "district": "Gwalior", "lat": 26.2183, "lon": 78.1828},
    {"name": "Vijayawada", "state": "Andhra Pradesh", "district": "Krishna", "lat": 16.5062, "lon": 80.6480},
    {"name": "Jodhpur", "state": "Rajasthan", "district": "Jodhpur", "lat": 26.2389, "lon": 73.0243},
    {"name": "Madurai", "state": "Tamil Nadu", "district": "Madurai", "lat": 9.9252, "lon": 78.1198},
    {"name": "Ranchi", "state": "Jharkhand", "district": "Ranchi", "lat": 23.3441, "lon": 85.3096},
    {"name": "Kochi", "state": "Kerala", "district": "Ernakulam", "lat": 9.9312, "lon": 76.2673},
    {"name": "Jamshedpur", "state": "Jharkhand", "district": "East Singhbhum", "lat": 22.8046, "lon": 86.2029},
    {"name": "Jalandhar", "state": "Punjab", "district": "Jalandhar", "lat": 31.3260, "lon": 75.5762},
    {"name": "Asansol", "state": "West Bengal", "district": "Paschim Bardhaman", "lat": 23.6734, "lon": 86.9517},
    {"name": "Dehradun", "state": "Uttarakhand", "district": "Dehradun", "lat": 30.3165, "lon": 78.0322},
    {"name": "Bhubaneswar", "state": "Odisha", "district": "Khordha", "lat": 20.2961, "lon": 85.8245},
    {"name": "Warangal", "state": "Telangana", "district": "Warangal Urban", "lat": 17.9784, "lon": 79.5941},
    {"name": "Guntur", "state": "Andhra Pradesh", "district": "Guntur", "lat": 16.3067, "lon": 80.4365},
    {"name": "Noida", "state": "Uttar Pradesh", "district": "Gautam Buddha Nagar", "lat": 28.5355, "lon": 77.3910},
    {"name": "Gurugram", "state": "Haryana", "district": "Gurugram", "lat": 28.4595, "lon": 77.0266},
    {"name": "Thiruvananthapuram", "state": "Kerala", "district": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366},
    {"name": "Mangaluru", "state": "Karnataka", "district": "Dakshina Kannada", "lat": 12.9141, "lon": 74.8560},
    {"name": "Mysuru", "state": "Karnataka", "district": "Mysuru", "lat": 12.2958, "lon": 76.6394},
    {"name": "Hubli-Dharwad", "state": "Karnataka", "district": "Dharwad", "lat": 15.3647, "lon": 75.1240},
    {"name": "Tiruppur", "state": "Tamil Nadu", "district": "Tiruppur", "lat": 11.1085, "lon": 77.3411},
    {"name": "Tiruchirapalli", "state": "Tamil Nadu", "district": "Tiruchirappalli", "lat": 10.7905, "lon": 78.7047},
    {"name": "Kolhapur", "state": "Maharashtra", "district": "Kolhapur", "lat": 16.7050, "lon": 74.2433},
    {"name": "Ajmer", "state": "Rajasthan", "district": "Ajmer", "lat": 26.4499, "lon": 74.6399},
    {"name": "Noida", "state": "Uttar Pradesh", "district": "Gautam Buddha Nagar", "lat": 28.5355, "lon": 77.3910},
    {"name": "Shimla", "state": "Himachal Pradesh", "district": "Shimla", "lat": 31.1048, "lon": 77.1734},
    {"name": "Gangtok", "state": "Sikkim", "district": "East Sikkim", "lat": 27.3314, "lon": 88.6138},
    {"name": "Itanagar", "state": "Arunachal Pradesh", "district": "Papum Pare", "lat": 27.0844, "lon": 93.6053},
    {"name": "Kohima", "state": "Nagaland", "district": "Kohima", "lat": 25.6701, "lon": 94.1077},
    {"name": "Aizawl", "state": "Mizoram", "district": "Aizawl", "lat": 23.7271, "lon": 92.7176},
    {"name": "Imphal", "state": "Manipur", "district": "Imphal West", "lat": 24.8170, "lon": 93.9368},
    {"name": "Shillong", "state": "Meghalaya", "district": "East Khasi Hills", "lat": 25.5788, "lon": 91.8933},
    {"name": "Guwahati", "state": "Assam", "district": "Kamrup Metropolitan", "lat": 26.1445, "lon": 91.7362},
    {"name": "Dispur", "state": "Assam", "district": "Kamrup Metropolitan", "lat": 26.1433, "lon": 91.7898},
    {"name": "Agartala", "state": "Tripura", "district": "West Tripura", "lat": 23.8315, "lon": 91.2868},
    {"name": "Panaji", "state": "Goa", "district": "North Goa", "lat": 15.4909, "lon": 73.8278},
    {"name": "Port Blair", "state": "Andaman & Nicobar", "district": "South Andaman", "lat": 11.6234, "lon": 92.7265},
    {"name": "Leh", "state": "Ladakh", "district": "Leh", "lat": 34.1526, "lon": 77.5771},
    {"name": "Puducherry", "state": "Puducherry", "district": "Pondicherry", "lat": 11.9416, "lon": 79.8083},
    {"name": "Chandigarh", "state": "Chandigarh", "district": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
]

INDIA_STATES = [
    "Andaman & Nicobar", "Andhra Pradesh", "Arunachal Pradesh", "Assam",
    "Bihar", "Chandigarh", "Chhattisgarh", "Dadra & Nagar Haveli",
    "Daman & Diu", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jammu & Kashmir", "Jharkhand", "Karnataka", "Kerala", "Ladakh",
    "Lakshadweep", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Puducherry", "Punjab", "Rajasthan",
    "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal",
]


def search_locations(query: str, limit: int = 10) -> list:
    """Search India locations by name, state, or district."""
    query_lower = query.lower().strip()
    if not query_lower:
        return []

    results = []
    for city in INDIA_CITIES:
        score = 0
        name_l = city["name"].lower()
        state_l = city["state"].lower()
        district_l = city["district"].lower()

        if query_lower == name_l:
            score = 100
        elif name_l.startswith(query_lower):
            score = 80
        elif query_lower in name_l:
            score = 60
        elif query_lower in state_l:
            score = 40
        elif query_lower in district_l:
            score = 30

        if score > 0:
            results.append((score, city))

    results.sort(key=lambda x: -x[0])
    return [r[1] for r in results[:limit]]
