import math

def haversine(a,b):
    la,lo,lb,lp=map(math.radians,(a['latitude'],a['longitude'],b['latitude'],b['longitude']))
    v=math.sin((lb-la)/2)**2+math.cos(la)*math.cos(lb)*math.sin((lp-lo)/2)**2
    return 6371.0088*2*math.asin(math.sqrt(max(0,min(1,v))))

def cost(route,matrix):
    return sum(matrix[a][b] for a,b in zip(route,route[1:]))

def nearest_neighbor(matrix):
    route=[0];remaining=set(range(1,len(matrix)))
    while remaining:
        nxt=min(remaining,key=lambda j:(matrix[route[-1]][j],j))
        route.append(nxt);remaining.remove(nxt)
    return route+[0]

def two_opt(route,matrix,max_passes=100):
    current=route[:]
    for _ in range(max_passes):
        best=current;best_cost=cost(current,matrix)
        for i in range(1,len(current)-2):
            for j in range(i+1,len(current)-1):
                candidate=current[:i]+current[i:j+1][::-1]+current[j+1:]
                value=cost(candidate,matrix)
                if value<best_cost-1e-10:
                    best,best_cost=candidate,value
        if best is current: break
        current=best
    return current
