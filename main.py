import asyncio
from tools.web_tools import search_news, read_article
from utils import state
from utils.web_functions import build_news_index 
from agents import Agent, RunConfig, Runner, AsyncOpenAI,OpenAIChatCompletionsModel,set_tracing_disabled
from rich.console import Console
from rich.markdown import Markdown
from rich import print
from rich.prompt import Prompt

set_tracing_disabled(True)

external_client = AsyncOpenAI(
    api_key="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",
    base_url="https://integrate.api.nvidia.com/v1"
)

agent = Agent(
    name="Lector de diarios digitales",
    instructions="""
    Eres un agente virtual que me ayuda a leer noticias, para esto cuentas con una 
    herramienta que busca en un indice local el contenido de noticas extraido de la pagina, 
    ,usa este indice para hacer resumen de los temas importantes y solo muestra esta informacion, no muestres urls o links 
    si no te lo pido especificamente, trata de retornar siempre algun resultado aunque
    no coincida con algun tema y aclara esto.
    Tambien cuentas con una herramienta para acceder a la nota completa en base a url que obtuvste del indice. 
    Quiero que hables en un tono amigable simulando que eres
    Argentino y usando lenguaje informal, siempre que te pida algo confirma que vas
    a comenzar una accion.
    Usa las herramientas para acceder a la informacion de la web, no intentes otro medio por ahora.
    """,
    tools=[
        search_news,
        #extract_links,
        read_article
    ],
    model= OpenAIChatCompletionsModel(
        model='qwen/qwen3.5-122b-a10b',
        openai_client=external_client)
)

state.news_index = build_news_index("https://www.quepasajujuy.com.ar")

async def main():
    console = Console()
    print(":face_with_tongue:","[bold blue]News Agent iniciado. Escribe 'salir' para terminar.\n")
    while True:
        #user_input = input("Tu: ")
        user_input = Prompt.ask(":hugging_face:[bold blue]Tu: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("Agente finalizado. :vulcan_salute:")
            break
        result = await Runner.run(agent, user_input)
        #print("\nAgente:", result.final_output)
        print("\n:robot: [bold green]Agente:")
        markdown = Markdown(result.final_output)
        console.print(markdown)
        print()
 
if __name__ == "__main__":
    asyncio.run(main())