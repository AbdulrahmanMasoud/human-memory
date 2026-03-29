"""FastAPI router for knowledge graph (semantic memory) operations."""

from fastapi import APIRouter, HTTPException, Request

from memory_system.models.graph import (
    ConceptCreate,
    ConceptResponse,
    ConsolidationReport,
    GraphSearchRequest,
    GraphSearchResult,
    RelationCreate,
    RelationResponse,
)

router = APIRouter(prefix="/v1/graph", tags=["graph"])


def _get_neo4j(request: Request):  # type: ignore[no-untyped-def]
    store = getattr(request.app.state, "neo4j_store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="Neo4j not available")
    return store


def _get_consolidation(request: Request):  # type: ignore[no-untyped-def]
    engine = getattr(request.app.state, "consolidation_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="Consolidation engine not available")
    return engine


@router.post("/concepts", response_model=ConceptResponse, status_code=201)
async def create_concept(body: ConceptCreate, request: Request) -> ConceptResponse:
    """Create or update a concept node."""
    store = _get_neo4j(request)
    result = await store.create_concept(body.name, body.type, body.activation)
    return ConceptResponse(name=result["name"], type=result["type"], activation=result["activation"])


@router.get("/concepts/{name}", response_model=ConceptResponse)
async def get_concept(name: str, request: Request) -> ConceptResponse:
    """Get a concept with its relationships."""
    store = _get_neo4j(request)
    result = await store.get_concept(name)
    if result is None:
        raise HTTPException(status_code=404, detail="Concept not found")

    relations = []
    for r in result.get("relations", []):
        if r.get("target"):
            relations.append(RelationResponse(
                source=name, target=r["target"],
                relation_type=r.get("type", "RELATED_TO"),
                weight=r.get("weight", 1.0),
            ))

    return ConceptResponse(
        name=result["name"], type=result["type"],
        activation=result["activation"], relationships=relations,
    )


@router.post("/relations", response_model=RelationResponse, status_code=201)
async def create_relation(body: RelationCreate, request: Request) -> RelationResponse:
    """Create a typed relationship between concepts."""
    store = _get_neo4j(request)
    result = await store.create_relation(body.source, body.target, body.relation_type, body.weight)
    if not result:
        raise HTTPException(status_code=404, detail="One or both concepts not found")
    return RelationResponse(**result)  # type: ignore[arg-type]


@router.post("/search", response_model=list[GraphSearchResult])
async def search_graph(body: GraphSearchRequest, request: Request) -> list[GraphSearchResult]:
    """Search the graph using spreading activation."""
    store = _get_neo4j(request)
    results = await store.spreading_activation(body.active_concepts, body.depth, body.limit)
    return [
        GraphSearchResult(name=r["name"], activation=r["activation"], path_weight=r["path_weight"])
        for r in results
    ]


@router.post("/consolidate", response_model=ConsolidationReport)
async def trigger_consolidation(request: Request) -> ConsolidationReport:
    """Manually trigger the consolidation cycle."""
    engine = _get_consolidation(request)
    return await engine.run_cycle()
