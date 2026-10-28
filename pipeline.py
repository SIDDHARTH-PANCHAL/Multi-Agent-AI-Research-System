from agents import build_search_agent, build_reader_agent , writer_chain , critic_chain

def run_research_pipeline(topic:str) -> dict:

  state = {}

  # search agent working 

  print("\n"+"="*50)
  print("step 1 - search agent is working . . .")
  print("="*50)

  search_agent = build_search_agent()
  search_result = search_agent.invoke({
    "messages" : [("user",f"find recent, reliable and detailed information about :{topic}")]
  })

  state['search_results'] = search_result['messages'][-1].content

  print("\n search results ",state['search_results'])


  # Reader agent

  print("\n"+"="*50)
  print("step 2 - Reader agen is scraping top resources . . .")
  print("="*50)

  reader_agent = build_reader_agent()
  reader_result = reader_agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                f"Research topic: {topic}\n\n"
                f"Search results:\n{state['search_results']}\n\n"
                "Select relevant URLs and scrape them using scrape_url. "
                "Summarize the evidence and preserve source URLs."
            ),
        }
    ]
})

  state['scraped_content'] = reader_result['messages'][-1].content

  print("\nscraped content\n",state['scraped_content'])


  # writer chain

  print("\n"+"="*50)
  print("step 3 - Writer is drafting the report . . .")
  print("="*50)


  research_combined = (
    f"SEARCH RESULTS :\n {state['search_results']}\n\n "
    f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
  )
  

  state["report"] = writer_chain.invoke({
    "topic": topic,
    "research" : research_combined
  })


  print("\n Final Report \n",state['report'])

  # critic report

  print("\n"+"=*50")
  print("step 4 - critic is reviewing the report.")
  print("="*50)

  state['feedback'] = critic_chain.invoke({
    "report" : state['report']
  })

  print("\n critic report \n",state['feedback'])

  return state


if __name__ == "__main__":
  topic = input("\n Enter a research topic : ")
  run_research_pipeline(topic)
   