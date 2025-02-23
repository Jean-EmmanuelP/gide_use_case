import os
import re

def is_simple_content(line):
    """
    Retourne True si la ligne représente du contenu simple (non formaté en titre).
    On considère qu'une ligne est du contenu simple si elle n'est pas vide
    et qu'elle ne commence pas par '#' ou '**'.
    """
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("#") or stripped.startswith("**"):
        return False
    return True

def count_headings(md_text):
    """
    Compte les titres en début de ligne :
      - Les titres Markdown (commençant par #)
      - Les titres en gras (**…**)
    Retourne un tuple (count_md, count_bold).
    """
    md_heading_pattern = re.compile(r'^(#{1,6})\s+(.*)$')
    bold_heading_pattern  = re.compile(r'^\*\*(.+)\*\*$')
    
    count_md = 0
    count_bold = 0

    for line in md_text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if md_heading_pattern.match(stripped):
            count_md += 1
        elif bold_heading_pattern.match(stripped):
            count_bold += 1
    return count_md, count_bold

def parse_headings_md(md_text):
    """
    Extrait les titres Markdown en début de ligne uniquement s'ils sont suivis
    d'une ligne de contenu simple.
    Retourne une liste de tuples (level, title).
    """
    md_heading_pattern = re.compile(r'^(#{1,6})\s+(.*)$')
    headings = []
    lines = md_text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        m = md_heading_pattern.match(stripped)
        if m:
            # Vérifier la présence d'une ligne de contenu simple immédiatement après
            j = i + 1
            found_content = False
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line:
                    if is_simple_content(next_line):
                        found_content = True
                    break
                j += 1
            if found_content:
                level = len(m.group(1))
                title = m.group(2).strip()
                headings.append((level, title))
    return headings

def parse_headings_bold(md_text):
    """
    Extrait les lignes en gras (**…**) en début de ligne uniquement s'il y a une
    ligne de contenu simple immédiatement après.
    On attribue un niveau fixe (ici 2) à ces titres.
    Retourne une liste de tuples (level, title).
    """
    bold_heading_pattern = re.compile(r'^\*\*(.+)\*\*$')
    headings = []
    lines = md_text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        m = bold_heading_pattern.match(stripped)
        if m:
            # Vérifier que la ligne suivante contient du contenu simple
            j = i + 1
            found_content = False
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line:
                    if is_simple_content(next_line):
                        found_content = True
                    break
                j += 1
            if found_content:
                title = m.group(1).strip()
                level = 2  # Niveau par défaut pour les titres en gras
                headings.append((level, title))
    return headings

def generate_toc(headings, doc_title=None):
    """
    Génère une table des matières en Markdown.
    - Si doc_title est fourni, il est affiché en en-tête.
    - Chaque titre est transformé en lien d'ancrage simplifié.
    """
    toc_lines = []
    if doc_title:
        toc_lines.append(f"# {doc_title}\n")
    toc_lines.append("## Table des Matières\n")
    for (level, title) in headings:
        indent = "  " * (level - 1)
        # Générer une ancre simplifiée (tout en minuscules, espaces et caractères spéciaux remplacés par des tirets)
        anchor = title.lower()
        anchor = re.sub(r"[^a-z0-9]+", "-", anchor).strip("-")
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    return "\n".join(toc_lines)

def generate_tocs_in_dir(directory):
    """
    Pour chaque fichier .md dans 'directory' :
      1. Analyse le contenu pour compter les titres Markdown et les titres en gras (en début de ligne).
      2. Choisit le style dominant.
      3. Extrait les titres correspondants, en ne gardant que ceux suivis d'une ligne de contenu simple.
      4. Considère le premier titre comme le titre principal du document et l'affiche en en-tête du TOC.
      5. Génère la TOC et l'enregistre dans un fichier <nom_fichier>_toc.md.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            md_path = os.path.join(directory, filename)
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Comptage des titres selon chaque style
            count_md, count_bold = count_headings(content)

            # Choix du style dominant
            if count_md > count_bold:
                headings = parse_headings_md(content)
                style_used = "Markdown (#)"
            elif count_bold > count_md:
                headings = parse_headings_bold(content)
                style_used = "Bold (**)"
            else:
                # En cas d'égalité, choisir Markdown par défaut
                headings = parse_headings_md(content)
                style_used = "Markdown (#) par défaut"
            
            # Le premier titre est considéré comme le titre principal
            if headings:
                doc_title = headings[0][1]
                toc_headings = headings[1:]
            else:
                doc_title = None
                toc_headings = []

            toc_content = generate_toc(toc_headings, doc_title=doc_title)
            
            # Écriture de la TOC dans un fichier séparé
            base_name, ext = os.path.splitext(filename)
            toc_filename = f"{base_name}_toc.md"
            toc_path = os.path.join(directory, toc_filename)
            with open(toc_path, 'w', encoding='utf-8') as f_out:
                f_out.write(toc_content)
            
            print(f"{filename}: style utilisé = {style_used}, TOC générée dans {toc_path}")

if __name__ == "__main__":
    output_dir = "docs/output"
    generate_tocs_in_dir(output_dir)
