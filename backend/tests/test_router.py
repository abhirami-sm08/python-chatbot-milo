from backend.rag.router import route_query

print(route_query("What is my EMI?",1001)[0])
print(route_query("Show my payment history",1001)[0])
print(route_query("What is a gold loan?",1001)[0])
print(route_query("Show my profile",1001)[0])