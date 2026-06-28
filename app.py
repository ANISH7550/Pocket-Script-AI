import streamlit as st
from google import genai
import sqlite3

conn = sqlite3.connect('scripts.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, idea TEXT, genre TEXT, script TEXT)')
conn.commit()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Pocket Script AI", page_icon="🎬")

st.title("🎬 Pocket Script AI")
st.write("Generate and save audio-ready scripts from simple ideas.")

st.sidebar.header("📜 Script History")
if st.sidebar.button("View Past Scripts"):
    c.execute('SELECT idea, genre, script FROM history ORDER BY id DESC LIMIT 5')
    saved_scripts = c.fetchall()
    if saved_scripts:
        for script in saved_scripts:
            with st.sidebar.expander(f"{script[1]}: {script[0][:20]}..."):
                st.write(script[2])
    else:
        st.sidebar.info("No scripts saved yet.")

story_idea = st.text_area("Enter your story idea:", "A detective finding a mysterious watch.")
genre = st.selectbox("Genre", ["Thriller", "Sci-Fi", "Romance", "Horror"])
tone = st.selectbox("Tone", ["Suspenseful", "Humorous", "Dark", "Dramatic"])

if st.button("Generate Script"):
    if story_idea:
        with st.spinner("Generating and saving your script..."):
            try:
                prompt = f"""
                You are an expert audio script writer for an entertainment platform.
                Convert the following story idea into a multi-character audio script.
                Include character names, dialogue, and specific audio/emotional cues in brackets like [Narrator, tense] or [Sound Effect: Door slams].
                
                Story Idea: {story_idea}
                Genre: {genre}
                Tone: {tone}
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                
                script_text = response.text
                
                c.execute('INSERT INTO history (idea, genre, script) VALUES (?, ?, ?)', (story_idea, genre, script_text))
                conn.commit()
                
                st.subheader("Generated Script:")
                st.write(script_text)
                st.success("Script successfully saved to database!")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a story idea first.")