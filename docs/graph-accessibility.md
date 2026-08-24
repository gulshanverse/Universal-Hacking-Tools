# Phase 9 Graph Accessibility

The interactive graph is an enhancement, never the only route to graph knowledge. Every explorer view includes an accessible relationship table grouped by entity type, conventional links to entity pages, visible focus states, and form controls for depth, relationship, type, and trust filters.

Keyboard users can select a center entity, expand a bounded neighborhood, change filters, request a shortest path, open an entity page, and inspect prerequisite and attack/defense sections without manipulating a canvas. The explorer announces selected entity, expansion, path-found, and truncation events through a polite live region. It does not expose raw SVG geometry to screen readers.

On small screens the list/panel order precedes the visual map, controls remain comfortably sized, and no graph action depends on hover. Motion is limited to opacity/transform transitions and disabled under `prefers-reduced-motion`. Node identity is communicated by text labels, entity-type labels, and icons or shape tokens rather than color alone.
