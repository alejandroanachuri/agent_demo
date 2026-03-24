import os
from dotenv import load_dotenv
import asyncio
from tools.web_tools import search_news_infobae, search_news_que_pasa_jujuy, read_article
from utils import state
from utils.web_functions import build_news_index 
from agents import Agent, RunConfig, Runner, AsyncOpenAI,OpenAIChatCompletionsModel,SQLiteSession, set_tracing_disabled
from rich.console import Console
from rich.markdown import Markdown
from rich import print
from rich.prompt import Prompt
from rich.rule import Rule

set_tracing_disabled(True)
load_dotenv()
nvidia_api_key = os.environ['NVIDIA_API_KEY']
external_client = AsyncOpenAI(
    api_key=nvidia_api_key,
    base_url="https://integrate.api.nvidia.com/v1"
)

agent = Agent(
    name="Lector de diarios digitales",
    instructions="""
    Eres un agente virtual que me ayuda a leer noticias, para esto cuentas con 
    herramientas que buscan en indices locales que contienen noticias de diarios digitales 
    ,usa estos indices segun el diario que te pida para hacer resumen de los temas 
    importantes y solo muestra esta informacion, no muestres urls o links si no te 
    lo pido especificamente, trata de retornar siempre algun resultado aunque
    no coincida con algun tema y aclara esto. Hay indices por cada diario digital.
    Tambien cuentas con una herramienta para acceder a la nota completa en base a url 
    que obtuviste del indice del diario digital correspondiente, si bien me vas a motrar
    un resumen de la pagina general tambien te voy a pedir que accedas a la nota, si hay varias
    notas que coinciden con el tema del resumen debes mostrarme el titulo de la notas asi 
    te puedo pedir la que corresponda. 
    Mi nombre es Ale y quiero que me hables en un tono amigable simulando que eres
    Argentino como yo, usando lenguaje informal y juvenil, siempre que te pida algo confirma que vas
    a comenzar una accion.
    Usa las herramientas para acceder a la informacion de la web, no intentes otro medio por ahora.
    """,
    tools=[
        search_news_infobae,
        search_news_que_pasa_jujuy,
        read_article
    ],
    model= OpenAIChatCompletionsModel(
        model='qwen/qwen3.5-122b-a10b',
        openai_client=external_client)
)

build_news_index("https://www.quepasajujuy.com.ar", "quepasajujuy", 
                 state.connection, state.cursor)
build_news_index("https://www.infobae.com/", "infobae", 
                 state.connection, state.cursor)

session = SQLiteSession("user_124")
async def main():
    console = Console()
    console.print(Rule(":face_with_tongue:[bold blue]News Agent iniciado. Escribe 'salir' para terminar.\n"))
    while True:
        #user_input = input("Tu: ")
        user_input = Prompt.ask(":hugging_face:[bold blue]Tu: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("Agente finalizado. :vulcan_salute:")
            break
        result = await Runner.run(agent, user_input, session=session)
        #print("\nAgente:", result.final_output)
        print("\n:robot: [bold green]Agente:")
        markdown = Markdown(result.final_output)
        console.print(markdown)
        print()
 
if __name__ == "__main__":
    asyncio.run(main())