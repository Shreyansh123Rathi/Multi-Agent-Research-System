from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

def run_research_pipeline(topic: str) -> dict:
    state = {}

    try:
        # Step 1 - Search Agent
        print("\n" + " =" * 50)
        print("Step 1 - Search agent is working ...")
        print("=" * 50)

        search_agent = build_search_agent()
        # FIX: Use "input" instead of "messages"
        search_result = search_agent.invoke({
            "input": f"Find recent, reliable and detailed information about: {topic}"
        })

       
        state["search_results"] = search_result["output"]
        print("\n Search completed.")
        print("\nSearch result:\n", state["search_results"])

    # Step 2 - Reader Agent 
        print("\n" + " =" * 50)
        print("Step 2 - Reader agent is scraping top resources ...")
        print("=" * 50)

        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "input": (
                f"Based on the following search results about '{topic}', "
                f"extract the single most relevant EXACT URL from the text and scrape it. "
                f"DO NOT guess, modify, or invent URLs. Only use URLs explicitly listed below.\n\n"
                f"Search Results:\n{state['search_results']}"
            )
        })
        state["scraped_content"] = reader_result["output"]
        print("\n Scraping completed.")


        # Step 3 - Writer Chain
        print("\n" + " =" * 50)
        print("Step 3 - Writer is drafting the report ...")
        print("=" * 50)

        research_combined = (
            f"SEARCH RESULTS :\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT :\n{state['scraped_content']}"
        )

        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })
        print("\nFinal Report:\n", state["report"])

        # Step 4 - Critic Review
        print("\n" + " =" * 50)
        print("Step 4 - Critic is reviewing the report ...")
        print("=" * 50)

        state["feedback"] = critic_chain.invoke({
            "report": state["report"]
        })
        print("\nCritic Report:\n", state["feedback"])

    except Exception as e:
        print(f"\n[!] An error occurred during the pipeline: {e}")
        state["error"] = str(e)

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)