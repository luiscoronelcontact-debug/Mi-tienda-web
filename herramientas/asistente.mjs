import OpenAI from "openai";

// Configurar solo en el entorno privado, nunca en archivos publicados.
const claveOpenRouter = process.env.OPENROUTER_API_KEY;
if (!claveOpenRouter) {
  console.error("Falta configurar OPENROUTER_API_KEY en el entorno privado.");
  process.exit(1);
}

const openai = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: claveOpenRouter,
  defaultHeaders: {
    "HTTP-Referer": "https://localhost:8000",
    "X-Title": "Cell Zone Assistant"
  }
});

const promptUsuario = process.argv.slice(2).join(" ");

if (!promptUsuario) {
  console.log("❌ Por favor, escribe lo que necesitas. Ejemplo:");
  console.log('node herramientas/asistente.mjs "agrega un banner de ofertas en index.html"');
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
