"""Semantic Light/Dark pairs shared by the native screens.

Blue identifies actions/selection; mint identifies progress. Status colors retain
text labels, and existing widgets resolve these pairs in place on appearance Save.
"""
COLORS = dict(
    bg=('#F8F7F3', '#0F172A'), sidebar=('#FFFFFF', '#111C30'),
    card=('#FFFFFF', '#162238'), raised=('#EAF0F7', '#243246'),
    border=('#8291A6', '#5B6F89'), accent=('#16805D', '#6EE7B7'),
    hover=('#1D4ED8', '#93C5FD'), primary=('#1D4ED8', '#1D4ED8'),
    primary_hover=('#1E40AF', '#1E40AF'), selected=('#DFEBFF', '#203858'),
    secondary_hover=('#DCE6F3', '#33465F'),
    text=('#172B4D', '#F1F5F9'), secondary=('#4B5D73', '#BBC9DB'),
    on_primary=('#FFFFFF', '#F8FAFC'), disabled_on_primary=('#DBEAFE', '#DBEAFE'),
    green=('#126B50', '#6EE7B7'), warning=('#8A4B08', '#FBBF24'),
    danger=('#B91C1C', '#991B1B'), danger_hover=('#991B1B', '#B91C1C'))
