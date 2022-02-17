

def by_string(query: str) -> list:
  return [{ "title": f"item{n}" } for n in range(0,50)]


def translate(raw_query: str) -> str:
  return raw_query


def embedd(query: str) -> list:
  return