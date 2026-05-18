import streamlit as st
import requests
import os

# Get backend URL from environment or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/chat")

st.title("🧠 RBAC RAG Chat System")

role = st.selectbox(
    'Select Your Role:',
    ('engineering', 'finance', 'general', 'hr', 'marketing')
)

question = st.text_area("Enter Your Question")

if st.button("Generate Answer"):

    if not question.strip():
        st.warning("Please enter a question")
    else:
        data = {
            "role": role,
            "question": question
        }

        try:
            with st.spinner("Generating answer..."):
                response = requests.post(BACKEND_URL, json=data, timeout=60)

            if response.status_code == 200:
                result = response.json()

                st.success("Answer:")
                st.write(result["response"])

                if result.get("source"):
                    st.info(f"Source: {result['source']}")

            elif response.status_code == 429:
                st.warning(f"⏳ Service Rate Limited\n\n{response.json().get('detail', 'Too many requests. Please wait a moment and try again.')}")
                st.info("💡 **Tip:** The Groq API has rate limits on free tier accounts (~30 requests/minute).\n- Wait 30-60 seconds before retrying\n- Consider upgrading to a paid tier for higher limits")
            elif response.status_code == 504:
                st.warning(f"⏱️ Request Timeout\n\n{response.json().get('detail', 'Request took too long. Please try again with a shorter question.')}")
            else:
                error_detail = response.json().get('detail', response.text) if response.text else f"HTTP {response.status_code}"
                st.error(f"API Error: {response.status_code}\n{error_detail}")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out (60 seconds). The backend may be busy or the API is slow. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to backend at {BACKEND_URL}\n\nMake sure the API server is running:\n```\nuvicorn backend.main:app --reload\n```")
        except Exception as e:
            st.error(f"Connection Error: {str(e)}")