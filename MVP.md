
1. Systemöversikt & Arkitektur
Applikationen byggs som en RAG-redo (Retrieval-Augmented Generation) plattform. Det innebär att vi först fokuserar på att indexera text så att den blir sökbar, vilket är förutsättningen för att senare kunna "prata" med dokumenten.

Komponent	Teknikstack (Exempel)	Syfte
Frontend	React eller Next.js	Webbgränssnitt för sök och uppladdning.
Backend	Python (FastAPI)	Hanterar logik, filuppladdning och sökalgoritmer.
Databas/Sök	ChromaDB eller Pinecone	En vektordatabas som lagrar kursmaterialet för smart sökning.
Övervakning	Prometheus & Grafana	Lokala verktyg för att se prestanda och loggar.
2. MVP-Funktioner (Fas 1)
Dokumenthantering & Indexering

Uppladdning: Ett enkelt drag-and-drop gränssnitt för PDF, Word och textfiler.

Textparsing: Systemet bryter ner kursmaterialet i mindre bitar ("chunks") för att göra sökningen träffsäker.

Lokal lagring: Allt material sparas lokalt eller i en säker molnmiljö för att behålla kontroll över dokumentationen.

Sökmotorn

Semantisk sökning: Istället för att bara söka på exakta ord (som Ctrl+F), förstår systemet kontext. Söker du på "examination" hittar den även "prov" eller "tentamen".

Resultatlista: Visar relevanta utdrag ur kursmaterialet med hänvisning till vilket dokument informationen kommer ifrån.

Lokal Övervakning (Monitoring)

För att dokumentera applikationens hälsa och användning lokalt implementeras:

Logging: En loggfil som sparar alla sökningar och eventuella fel.

Dashboard: En enkel sida (via t.ex. Streamlit eller Grafana) som visar:

Antal indexerade dokument.

Svarstid på sökningar.

Systemresurser (CPU/RAM-användning).

3. Vidareutveckling (Fas 2: AI-Chatt)
När sökfunktionen fungerar, adderas "hjärnan":

Konversations-AI: Genom att koppla en LLM (t.ex. GPT-4 eller en lokal Llama-modell) till din sökbas kan användaren ställa frågor som: "Sammanfatta vad kursmaterialet säger om källkritik".

Källhänvisning: AI:n svarar inte bara, utan pekar direkt på vilken sida i kursdokumenten den hämtat infon ifrån.