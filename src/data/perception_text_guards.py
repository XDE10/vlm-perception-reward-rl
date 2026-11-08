"""Conservative finite prose entailments; a non-match is NOT image exclusivity."""
import re
def entailed_by_prose(problem,fact):
    rel=fact['relation'];e=fact['entities'];value=fact.get('value','')
    plain=re.sub(r'\\(?:overline|triangle|square|angle|widehat|mathrm|text|cong)\b',' ',problem)
    plain=re.sub(r'[$\\{}]',' ',plain);plain=re.sub(r'\s+',' ',plain)
    shape=re.search(r'(?i:\b(rhombus|parallelogram|rectangle|square|trapezoid|quadrilateral))\s+([A-Z](?:\s*[A-Z]){3})\b',plain)
    reversed_shape=re.search(r'\b([A-Z](?:\s*[A-Z]){3})\s+(?i:is|forms)\s+(?i:an?|the)\s+(?i:(rhombus|parallelogram|rectangle|square|trapezoid|quadrilateral))\b',plain)
    def line(x):return frozenset(x) if isinstance(x,(list,tuple)) and len(x)==2 else None
    if shape or reversed_shape:
        name=(shape.group(1) if shape else reversed_shape.group(2)).lower();v=re.sub(r'\s','',shape.group(2) if shape else reversed_shape.group(1));edges=[frozenset((v[i],v[(i+1)%4])) for i in range(4)];diags=[frozenset((v[0],v[2])),frozenset((v[1],v[3]))]
        if name in {'rectangle','square'} and rel=='Perpendicular' and len(e)==2:
            if any({line(x) for x in e}=={edges[i],edges[(i+1)%4]} for i in range(4)):return 'rectangle_or_square_adjacent_edges_perpendicular_from_text'
        intersection=re.search(r'(?i:\bdiagonals\b.*?\b(?:intersect|meet|cross)\s+(?:at|in))\s+([A-Z])\b',plain)
        if intersection and rel=='PointLiesOnLine' and e[0]==intersection.group(1) and line(e[1]) in diags:return 'prose_named_quadrilateral_diagonals_intersect_at_point'
        if name in {'rhombus','square'} and rel=='Perpendicular' and {line(x) for x in e}==set(diags):return 'rhombus_or_square_diagonals_perpendicular_from_text'
        if name in {'rectangle','square'} and rel=='Angle' and value=='90' and len(e)==3:
            for i in range(4):
                if e[1]==v[i] and set((e[0],e[2]))=={v[(i-1)%4],v[(i+1)%4]}:return 'rectangle_or_square_right_angle_from_text'
        if name in {'rhombus','square'} and rel=='CongruentLength' and all(line(x) in edges for x in e):return 'rhombus_or_square_equal_sides_from_text'
        if name in {'rhombus','square','parallelogram','rectangle'} and rel=='Parallel':
            if {line(x) for x in e} in [{edges[0],edges[2]},{edges[1],edges[3]}]:return 'parallelogram_opposite_edges_parallel_from_text'
    if rel=='PointLiesOnLine':
        m=re.search(r'([A-Z])\s*(?i:is (?:the )?midpoint of)\s*([A-Z])\s*([A-Z])',plain)
        if m and e[0]==m.group(1) and line(e[1])==frozenset(m.group(2)+m.group(3)):return 'midpoint_incidence_from_prose'
        m=re.search(r'([A-Z])\s*([A-Z])\s+(?i:and)\s+([A-Z])\s*([A-Z])\s+(?i:intersect at)\s+([A-Z])',plain)
        if m and e[0]==m.group(5) and line(e[1]) in {frozenset(m.group(1)+m.group(2)),frozenset(m.group(3)+m.group(4))}:return 'named_lines_intersect_at_point_from_prose'
    if rel=='PointLiesOnCircle' and isinstance(e[1],dict):
        circles=re.findall(r'(?:\\odot|(?i:\bcircle))\s*\{?\s*([A-Z])',problem)
        arcs=re.findall(r'\\(?:widehat|overarc)\s*\{\s*([A-Z](?:\s*[A-Z]){1,2})\s*\}|(?i:\barc)\s+([A-Z]{2,3})\b',problem)
        points=set(''.join(''.join(x) for x in arcs).replace(' ',''))
        if len(set(circles))==1 and e[1]['center']==circles[0] and e[0] in points:return 'named_arc_points_on_named_circle_entailed_by_text'
    return None
