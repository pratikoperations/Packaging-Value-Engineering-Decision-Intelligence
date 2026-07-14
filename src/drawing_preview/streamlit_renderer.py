from __future__ import annotations

import html
from typing import Any

from .models import PreviewDescriptor


def render_preview(st: Any, descriptor: PreviewDescriptor, *, height: int = 620) -> None:
    """Render a governed preview through a Streamlit-compatible interface."""
    st.caption(
        f"{descriptor.metadata.get('classification', 'unclassified').title()} — "
        f"{descriptor.metadata.get('document_number', 'Unknown document')} "
        f"Rev {descriptor.metadata.get('revision', 'N/A')}"
    )
    st.json(descriptor.metadata, expanded=False)

    if descriptor.available and descriptor.mode == "image":
        st.image(descriptor.payload, width="stretch")
    elif descriptor.available and descriptor.mode == "svg":
        st.image(descriptor.payload, width="stretch")
    elif descriptor.available and descriptor.mode == "pdf_embed":
        source = f"data:application/pdf;base64,{descriptor.payload}"
        st.markdown(
            f'<iframe src="{source}" width="100%" height="{int(height)}" '
            'style="border:1px solid #ddd" title="Governed PDF preview"></iframe>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Inline preview unavailable. The governed metadata and source reference remain visible.")
        for issue in descriptor.issues:
            st.write(f"- {html.escape(issue.message)}")

    st.warning(" ".join(descriptor.limitations))
