import os
import re

def is_simple_content(line):
    """
    Retourne True si la ligne représente du contenu simple (texte normal).
    Une ligne est considérée comme du contenu simple si elle n'est pas vide
    et ne commence ni par '#' ni par '**'.
    """
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("#") or stripped.startswith("**"):
        return False
    return True

def count_headings(md_text):
    """
    Parcourt l'ensemble du texte et compte les titres en début de ligne :
      - Titres Markdown (commençant par #)
      - Titres en gras (délimités par **)
    Retourne un tuple (count_md, count_bold).
    """
    md_heading_pattern = re.compile(r'^(#{1,6})\s+(.*)$')
    bold_heading_pattern = re.compile(r'^\*\*(.+)\*\*$')
    
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

def get_first_heading(md_text):
    """
    Parcourt le document pour trouver le tout premier titre (Markdown ou Bold)
    en début de ligne et le retourne sous forme d'un tuple (index, style, level, title).
    Si aucun titre n'est trouvé, retourne (None, None).
    """
    md_heading_pattern = re.compile(r'^(#{1,6})\s+(.*)$')
    bold_heading_pattern = re.compile(r'^\*\*(.+)\*\*$')
    lines = md_text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        m_md = md_heading_pattern.match(stripped)
        if m_md:
            level = len(m_md.group(1))
            title = m_md.group(2).strip()
            return i, ("md", level, title)
        m_bold = bold_heading_pattern.match(stripped)
        if m_bold:
            # Pour les titres en gras, on attribue un niveau fixe (ici 2)
            level = 2
            title = m_bold.group(1).strip()
            return i, ("bold", level, title)
    return None, None

def parse_headings_md(md_text, start_index):
    """
    Extrait les titres Markdown en début de ligne à partir de start_index+1,
    mais uniquement s'ils sont suivis d'une ligne de contenu simple.
    Retourne une liste de tuples (level, title).
    """
    md_heading_pattern = re.compile(r'^(#{1,6})\s+(.*)$')
    headings = []
    lines = md_text.split('\n')
    for i, line in enumerate(lines):
        if i <= start_index:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        m = md_heading_pattern.match(stripped)
        if m:
            title = m.group(2).strip()
            level = len(m.group(1))
            # Vérifier la présence d'une ligne de contenu simple après ce titre
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
                headings.append((level, title))
    return headings

def parse_headings_bold(md_text, start_index):
    """
    Extrait les titres en gras (délimités par **…) en début de ligne à partir de start_index+1,
    mais uniquement s'ils sont suivis d'une ligne de contenu simple.
    On attribue ici un niveau fixe (2) aux titres en gras.
    Retourne une liste de tuples (level, title).
    """
    bold_heading_pattern = re.compile(r'^\*\*(.+)\*\*$')
    headings = []
    lines = md_text.split('\n')
    for i, line in enumerate(lines):
        if i <= start_index:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        m = bold_heading_pattern.match(stripped)
        if m:
            title = m.group(1).strip()
            level = 2
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
                headings.append((level, title))
    return headings

def generate_toc(headings, doc_title=None):
    """
    Génère la table des matières en Markdown.
    - Si doc_title est fourni, il est affiché en en-tête (niveau 1).
    - Chaque titre est transformé en lien d'ancrage simplifié.
    La TOC ne contient pas de ligne "## Table des Matières".
    """
    toc_lines = []
    if doc_title:
        toc_lines.append(f"# {doc_title}")
        toc_lines.append("")  # Ligne vide pour séparer le titre principal de la liste
    for (level, title) in headings:
        indent = "  " * (level - 1)
        # Création d'une ancre simplifiée : tout en minuscules, les caractères non alphanumériques remplacés par des tirets
        anchor = title.lower()
        anchor = re.sub(r"[^a-z0-9]+", "-", anchor).strip("-")
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    return "\n".join(toc_lines)

def generate_tocs_in_dir(directory):
    """
    Pour chaque fichier .md dans 'directory' :
      1. Analyse le contenu pour extraire le premier titre (peu importe le style), qui sera le titre principal.
      2. Compte les titres par style dans le document.
      3. Choisit le style dominant pour le reste du document.
      4. Extrait les titres (à partir de la ligne suivante du premier titre) qui respectent les règles :
         - Titre en début de ligne du style choisi.
         - Suivi d'une ligne de contenu simple.
      5. Génère la TOC avec le titre principal en tête et les titres extraits.
      6. Enregistre la TOC dans un fichier <nom_fichier>_toc.md.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            md_path = os.path.join(directory, filename)
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraction du tout premier titre (quelle que soit sa forme)
            first_index, first_heading = get_first_heading(content)
            if first_heading:
                doc_title = first_heading[2]  # Le titre principal
            else:
                doc_title = None
                first_index = -1  # Aucun titre trouvé
            
            # Comptage des titres sur l'ensemble du document
            count_md, count_bold = count_headings(content)
            
            # Choix du style dominant pour les titres à partir du premier
            if count_md > count_bold:
                headings = parse_headings_md(content, start_index=first_index)
                style_used = "Markdown (#)"
            elif count_bold > count_md:
                headings = parse_headings_bold(content, start_index=first_index)
                style_used = "Bold (**)"
            else:
                # En cas d'égalité, choisir Markdown par défaut
                headings = parse_headings_md(content, start_index=first_index)
                style_used = "Markdown (#) par défaut"
            
            # La TOC utilisera le titre principal en en-tête, et les autres titres en liste
            toc_content = generate_toc(headings, doc_title=doc_title)
            
            # Écriture de la TOC dans un fichier séparé (<nom_fichier>_toc.md)
            base_name, ext = os.path.splitext(filename)
            toc_filename = f"{base_name}_toc.md"
            toc_path = os.path.join(directory, toc_filename)
            with open(toc_path, 'w', encoding='utf-8') as f_out:
                f_out.write(toc_content)
            
            print(f"{filename}: style utilisé = {style_used}, TOC générée dans {toc_path}")

if __name__ == "__main__":
    output_dir = "docs/output"
    generate_tocs_in_dir(output_dir)
