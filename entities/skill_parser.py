from utils.common import get_skill_rank_data

class SkillParserMixin:
  def parse_skills(self, cells: list, headers: list, skills_lookup: dict[str, int]) -> list[dict]:
    skills = []

    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    skill_columns = self._find_skill_columns(headers)

    for skill_name_col, skill_level_col in skill_columns:
      name = get_cell_text(skill_name_col)
      level_str = get_cell_text(skill_level_col)

      # if name is empty, then skill/level doesn't exist for weapon
      if not name: 
        continue

      try:
        level = int(level_str)

        if name in skills_lookup:
          skill_id = skills_lookup[name]
          skill_rank = get_skill_rank_data(skill_id, level)

          if skill_rank:
            skills.append({
              'id': skill_rank['id']
            })
            print(f"Added skill: {name} level {level} (rank id: {skill_rank['id']})")
          else:
            print(f"Warning: Could not find skill rank data for {name} level {level}")
      
      except ValueError as e:
        print(f"Warning: Could not parse skill level '{level}' for skill '{name}': {e}")
        continue

    return skills
    
  # helper method
  def _find_skill_columns(self, headers: list) -> list[tuple[int, int]]:
    skill_columns = []
    
    # lowercase headers
    headers_lower = [header.lower() for header in headers]
    
    skill_patterns = [
      ('skill 1', 'skill 1 level'),
      ('skill 2', 'skill 2 level'),
    ]
        
    for skill_header, level_header in skill_patterns:
      try:
        skill_name_col = headers_lower.index(skill_header)
        skill_level_col = headers_lower.index(level_header)
        skill_columns.append((skill_name_col, skill_level_col))
      except ValueError:
        print(f"Could not find pattern: {skill_header} / {level_header}")
        continue
        
    return skill_columns