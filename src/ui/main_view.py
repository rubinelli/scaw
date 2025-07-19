import streamlit as st
import graphviz
from sqlalchemy.orm import Session
from database.models import LogEntry, MapPoint, Path


def render_main_view(db: Session):
    """Renders the main adventure log and context view."""
    st.title("Adventure Log")
    _render_context_view(db)
    _render_session_view(db)
    _render_user_input(db)


def _render_context_view(db: Session):
    """Renders the top-level context view with the map."""
    with st.container(border=True):
        st.subheader("Context View")
        st.write("**Map View**")
        map_container = st.container(border=True)
        _render_map(map_container, db)


def _render_map(container, db: Session):
    """Renders the world map using Graphviz, showing only known/explored areas."""
    # Define colors for different statuses
    STATUS_COLORS = {
        "explored": "#aaffaa",  # Light green
        "known": "#lightblue2",  # Default blue
        "rumored": "#dddddd",  # Light grey (for potential future use)
        "hidden": "#ffffff",  # White (invisible)
    }
    EDGE_STATUS_COLORS = {
        "explored": "green",
        "known": "gray40",
        "hidden": "transparent",
    }

    # Fetch only the map points and paths that should be visible
    visible_map_points = (
        db.query(MapPoint).filter(MapPoint.status.in_(["known", "explored"])).all()
    )
    visible_paths = db.query(Path).filter(Path.status.in_(["known", "explored"])).all()

    if not visible_map_points:
        container.write("The world map is yet to be discovered.")
        return

    dot = graphviz.Digraph("WorldMap", comment="The Known World")
    dot.attr("graph", bgcolor="transparent", rankdir="TB")
    dot.attr("node", shape="box", style="rounded,filled")
    dot.attr("edge")  # Remove default color

    # Add nodes to the graph with status-based colors
    for point in visible_map_points:
        node_label = f"{point.name}\n({point.type})"
        fill_color = STATUS_COLORS.get(point.status, "#ffffff")
        dot.node(str(point.id), node_label, fillcolor=fill_color)

    # Add edges to the graph with status-based colors
    for path in visible_paths:
        # Ensure both ends of the path are visible before drawing
        start_point_visible = any(
            p.id == path.start_point_id for p in visible_map_points
        )
        end_point_visible = any(p.id == path.end_point_id for p in visible_map_points)

        if start_point_visible and end_point_visible:
            edge_color = EDGE_STATUS_COLORS.get(path.status, "transparent")
            dot.edge(str(path.start_point_id), str(path.end_point_id), color=edge_color)

    container.graphviz_chart(dot)


def _render_session_view(db: Session):
    """Renders the chat-style log of game events."""
    st.subheader("Session View")
    log_container = st.container(border=True, height=400)
    log_entries = db.query(LogEntry).order_by(LogEntry.created_at.asc()).all()
    for entry in log_entries:
        with log_container.chat_message(name=entry.source.lower()):
            st.markdown(entry.content)
            if entry.metadata_dict and entry.metadata_dict.get("requires_saving_throw"):
                if st.button("Roll Saving Throw", key=f"saving_throw_{entry.id}"):
                    st.session_state.orchestrator.handle_player_input(
                        "roll saving throw", db
                    )
                    st.rerun()


def _render_user_input(db: Session):
    """Renders the user input bar."""
    if prompt := st.chat_input("What do you do?"):
        st.session_state.orchestrator.handle_player_input(prompt, db)
        st.rerun()
