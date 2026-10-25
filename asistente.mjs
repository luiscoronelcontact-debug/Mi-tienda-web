import OpenAI from "openai";

const openai = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: "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",
  defaultHeaders: {
    "HTTP-Referer": "https://localhost:8000",
    "X-Title": "Cell Zone Assistant"
  }
});

const promptUsuario = process.argv.slice(2).join(" ");

if (!promptUsuario) {
  console.log("❌ Por favor, escribe lo que necesitas. Ejemplo:");
  console.log('node asistente.mjs "agrega un banner de ofertas en index.html"');
  process.exit(1);
}

async function consultarAsistente() {
  try {
    console.log("🤖 Qwen está procesando tu solicitud para CELL ZONE...\n");
    const completion = await openai.chat.completions.create({
      model: "qwen/qwen-2.5-coder-32b-instruct",
      messages: [
        { 
          role: "system", 
          content: "Eres un desarrollador experto en frontend ayudando a construir la tienda web 'CELL ZONE' (HTML, Tailwind CSS, JavaScript). Devuelve el código limpio y listo para usar según lo que solicite el usuario." 
        },
        { role: "user", content: promptUsuario }
      ]
    });
    console.log(completion.choices[0].message.content);
  } catch (err) {
    console.error("Error al conectar:", err.message);
  }
}

consultarAsistente();
