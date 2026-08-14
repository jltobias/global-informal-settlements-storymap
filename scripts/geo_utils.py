from __future__ import annotations
import math

def iter_xy(coords):
    if not isinstance(coords, list):
        return
    if coords and isinstance(coords[0], (int,float)) and len(coords)>=2:
        yield float(coords[0]), float(coords[1]); return
    for child in coords:
        yield from iter_xy(child)

def geometry_bbox(geometry):
    pts=list(iter_xy((geometry or {}).get('coordinates', [])))
    if not pts: return None
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return [min(xs),min(ys),max(xs),max(ys)]

def representative_point(geometry):
    bbox=geometry_bbox(geometry)
    if bbox is None: return None
    return [(bbox[0]+bbox[2])/2.0,(bbox[1]+bbox[3])/2.0]

def bbox_polygon(bbox):
    a,b,c,d=bbox
    return {'type':'Polygon','coordinates':[[[a,b],[c,b],[c,d],[a,d],[a,b]]]}

def lonlat_to_webmercator(lon,lat):
    lat=max(min(float(lat),85.05112878),-85.05112878)
    x=float(lon)*20037508.34/180.0
    y=math.log(math.tan((90.0+lat)*math.pi/360.0))/(math.pi/180.0)
    y=y*20037508.34/180.0
    return x,y

def bbox_to_webmercator(bbox,pad=0.12):
    xmin,ymin,xmax,ymax=bbox
    dx=max(xmax-xmin,0.002); dy=max(ymax-ymin,0.002)
    xmin-=dx*pad; xmax+=dx*pad; ymin-=dy*pad; ymax+=dy*pad
    x1,y1=lonlat_to_webmercator(xmin,ymin); x2,y2=lonlat_to_webmercator(xmax,ymax)
    return [min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)]
