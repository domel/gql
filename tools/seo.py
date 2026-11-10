#!/usr/bin/env python3
"""Apply SEO to the HTML edition only; safe to rerun after HTML conversion."""
from pathlib import Path
import html
import json
import re
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from cover import update_home_cover

SITE = Path(__file__).resolve().parents[1]
BASE = 'https://gql.fyi/'
META = {
    'index.html': ('GQL (Graph Query Language) | GQL Essentials - Free Online Book', 'Learn GQL (Graph Query Language), ISO/IEC 39075, with a free online book by Dominik Tomaszuk. Explore syntax, query examples, graph patterns and schemas.'),
    '01-history.html': ('GQL History: From Graph Databases to an ISO Standard', 'Trace the history of Graph Query Language, from graph database research and earlier query languages to the ISO/IEC 39075 GQL standard.'),
    '02-property-graph-databases.html': ('Property Graph Databases: Concepts and Use Cases', 'Understand property graph databases, their applications and limitations, and the role of nodes, edges and properties in the GQL data model.'),
    '03-positioning.html': ('GQL vs SQL, SPARQL and Other Database Languages', 'Compare the foundations of GQL with SQL, RDF and SPARQL, tree-based languages, and document databases through the running library example.'),
    '04-gql-by-example.html': ('GQL Tutorial with Examples: Queries and Graph Patterns', 'Learn GQL through a library graph: define graph types, insert data and write MATCH queries with filters, paths, aggregation and ordering.'),
    '05-a-conceptual-glossary-of-gql.html': ('GQL Glossary: Graphs, Queries, Types and Semantics', 'Look up GQL concepts, from property graphs, values and paths to binding tables, schemas, constraints, transactions and authorization.'),
    '06-data-model.html': ('GQL Data Model: Nodes, Edges and Property Graphs', 'Study the GQL property graph model, node and edge identities, labels, property values, types, paths, lists and structural access.'),
    '07-patterns-and-matching.html': ('GQL Pattern Matching: MATCH and Graph Patterns', 'Explore GQL MATCH syntax and semantics: graph patterns, variable exposure, binding tables, scopes and the conditions for finite matching.'),
    '08-expressions-and-evaluation.html': ('GQL Expressions: Evaluation, Types and NULL', 'Understand GQL expression evaluation, typing rules, truth values and NULL, with a formal account of expressions over graph query bindings.'),
    '09-algebra-of-binding-tables.html': ('GQL Binding Tables: Joins, OPTIONAL and Query Algebra', 'Study selection, projection, joins, OPTIONAL, FOR, subqueries and set operators in the algebra underlying GQL binding tables.'),
    '10-path-semantics.html': ('GQL Path Semantics: Walk, Trail, Simple and Acyclic', 'Understand GQL path modes, finiteness, path selection and accessors, including the distinctions between walk, trail, simple and acyclic paths.'),
    '11-regular-path-expressions.html': ('GQL Regular Path Expressions and Shortest Paths', 'Learn the syntax and denotation of GQL regular path expressions, repeated graph patterns and the semantics of shortest-path selection.'),
    '12-grouping-and-aggregation.html': ('GQL Aggregation: GROUP BY, HAVING and DISTINCT', 'Learn how grouping and aggregates shape GQL query results, including GROUP BY, HAVING, DISTINCT and primitive result statements.'),
    '13-ordering-and-pagination.html': ('GQL ORDER BY, LIMIT and OFFSET: Ordering Results', 'Understand ordering and pagination in GQL, including peer ordering, deterministic results and the semantics of LIMIT and OFFSET.'),
    '14-data-modification.html': ('GQL Data Modification: INSERT, SET and DELETE', 'Explore GQL graph updates, read-then-update queries, write conflicts and constraint validation through examples and a formal update model.'),
    '15-types-and-schemas.html': ('GQL Types and Graph Schemas', 'Study GQL property, node, edge and graph types, constraining graph types, schema definitions, DDL semantics and schema versioning.'),
    '16-constraints.html': ('GQL Constraints: Keys, Uniqueness and Enforcement', 'Explore graph keys and uniqueness, constraint enforcement, effects and write-purity in the formal model presented in GQL Essentials.'),
    '17-catalog-names-and-session-state.html': ('GQL Catalogs, Names and Session State', 'Understand named graph objects, namespaces, qualified references, USE and session state in GQL, with formal definitions and examples.'),
    '18-procedures.html': ('GQL Procedures: Signatures, Calls and Scope', 'Study GQL procedure signatures, body typing, procedure calls and scoping, and how routines interact with graph query evaluation.'),
    '19-transaction-model.html': ('GQL Transactions: Isolation, Visibility and Aborts', 'Explore transaction demarcation, visibility, serializability, isolation and aborts in the transaction model developed in GQL Essentials.'),
    '20-authorization.html': ('GQL Authorization: Roles, Privileges and Access', 'Understand roles, privileges, access checks and write checks in the formal authorization model developed in GQL Essentials.'),
    '21-diagnostics.html': ('GQL Diagnostics: Errors, Exceptions and Status Codes', 'Study GQL errors, exceptions, status codes and control flow, and how diagnostics relate to query execution and transaction behavior.'),
    '22-future-enhancements.html': ('GQL Future Enhancements: Composition and Schemas', 'Examine proposed directions for GQL, including compositional queries, graph schemas, data model extensions and integration with AI.'),
    '23-research-directions.html': ('GQL Research: Expressiveness and Query Optimization', 'Explore research questions in GQL expressiveness, complexity, optimization, transactions, graph-to-graph queries and interoperability.'),
    'contents.html': ('GQL Essentials: Detailed Table of Contents', 'Browse all 23 chapters and their sections in GQL Essentials, from graph query examples and pattern matching to schemas and transactions.'),
    'book-overview.html': ('GQL Essentials: Book Overview and Reading Guide', 'Find out how GQL Essentials is organized and how its examples, definitions and formal semantics support learning Graph Query Language.'),
    'bibliography.html': ('GQL Bibliography: Standards and Graph Database Research', 'Find the standards, papers and books cited in GQL Essentials, with references on graph query languages, databases and formal semantics.'),
    'acronyms.html': ('GQL Acronyms and Database Abbreviations', 'Look up the acronyms used in GQL Essentials, including database terminology and abbreviations relevant to Graph Query Language.'),
    'symbols-and-notations.html': ('GQL Symbols and Mathematical Notation', 'Consult the symbols and mathematical notation used to define the data model and query semantics in GQL Essentials.'),
    'subject-index.html': ('GQL Essentials: Subject Index', 'Find GQL concepts in the subject index, with links to the chapters and sections that explain each term.'),
    'publication-details.html': ('GQL Essentials: Publication Details, ISBN and DOI', 'Publication details for GQL Essentials by Dominik Tomaszuk: author ORCID, publisher, reviewers, ISBN 978-83-7431-884-6 and DOI.'),
    'acknowledgments.html': ('GQL Essentials: Acknowledgments', 'Read the author acknowledgments in GQL Essentials, the free online book on Graph Query Language by Dominik Tomaszuk.'),
    'footnote-6.html': ('GQL Essentials: SPARQL Acronym Note', 'A note explaining the SPARQL acronym in GQL Essentials.'),
    'footnote-17.html': ('GQL Essentials: Paging Operators Note', 'A note on paging operators and slice semantics in GQL Essentials.'),
}

def code(text, language='GQL'):
    return '<div class="code-wrap"><div class="code-label">' + language + '</div><button class="copy-code" aria-label="Copy code">Copy</button><pre tabindex="0"><code>' + html.escape(text) + '</code></pre></div>'

GUIDES = {}
def guide(slug, title, description, body):
    filename = slug + '.html'
    META[filename] = (title, description)
    GUIDES[filename] = body

guide('what-is-gql', 'What Is GQL? Graph Query Language Explained',
      'Learn what GQL is, how property graphs work and how Graph Query Language relates to SQL, Cypher and GraphQL. Start with a short query example.', '''
<p>GQL stands for Graph Query Language. It is a database language for property graphs, standardized as ISO/IEC 39075:2024. A property graph stores entities as nodes and connections as edges; both can carry labels and properties.</p>
<h2>A graph represents relationships directly</h2>
<p>In a library, a loan can connect to a book through an <code>INCLUDES</code> edge. The book node stores its title and ISBN. The edge can store a due date and a late fee, because these describe a particular borrowing rather than the book itself.</p>
<p>GQL lets a query describe this connection as a pattern. Parentheses describe nodes, brackets describe edges, and arrows describe their direction.</p>
''' + code("MATCH (l:Loan)-[i:INCLUDES]->(b:Book)\nWHERE i.late_fee > 0.0\nRETURN l.loanid AS loan, b.title AS title") + '''
<p>For each matching loan-to-book connection with a positive late fee, this query returns the loan identifier and book title. It assumes the library graph is already selected. The names <code>l</code>, <code>i</code> and <code>b</code> bind the matched elements so later clauses can access their properties.</p>
<h2>What does GQL cover?</h2>
<p>Its scope includes querying and changing graph data, defining graph structures and controlling access. Query results can be binding tables: rows whose columns contain the values bound during evaluation. Learn the structure in <a href="06-data-model.html">the data model chapter</a> and the matching rules in <a href="07-patterns-and-matching.html">Patterns and Matching</a>.</p>
<h2>GQL, Cypher and GraphQL</h2>
<p>Cypher and GQL share familiar pattern syntax, but compatibility depends on the implementation and feature. <a href="gql-vs-cypher.html">Compare GQL and Cypher</a> before moving queries between systems. GraphQL is a separate API query language; this book concerns the database language GQL.</p>
<h2>Where to start</h2>
<p>Follow the <a href="gql-tutorial.html">beginner tutorial</a> for a guided query, or read <a href="04-gql-by-example.html">GQL by Example</a> for the complete library setup. The <a href="https://www.iso.org/standard/76120.html">ISO standard record</a> identifies the specification; GQL Essentials is an independent explanation of its concepts.</p>
''')

guide('gql-tutorial', 'GQL Tutorial for Beginners: Your First Graph Query',
      'Write your first GQL query using MATCH, WHERE and RETURN. Follow a library example, read the results and continue to the complete graph setup.', '''
<p>This tutorial reads a small library graph. It assumes <code>libraryGraph</code> has been created and populated as in <a href="04-gql-by-example.html">Chapter 4</a>. The examples describe query behavior; running them requires a database that supports the GQL features used here.</p>
<h2>1. Identify nodes and edges</h2>
<p>A <code>Loan</code> node has a <code>loanid</code>. A <code>Book</code> node has a <code>title</code>. An <code>INCLUDES</code> edge connects a loan to a borrowed book and carries <code>due_date</code> and <code>late_fee</code> properties. One loan may include several books.</p>
<h2>2. Match a connection</h2>
''' + code('USE libraryGraph\nMATCH (l:Loan)-[i:INCLUDES]->(b:Book)\nRETURN l.loanid AS loan, b.title AS title') + '''
<p><code>USE</code> selects the graph. <code>MATCH</code> finds directed connections with the stated labels. <code>RETURN</code> chooses the output columns, and <code>AS</code> names them. A loan with two included books produces two matches, so its identifier can appear in two result rows.</p>
<h2>3. Filter by an edge property</h2>
''' + code('USE libraryGraph\nMATCH (l:Loan)-[i:INCLUDES]->(b:Book)\nWHERE i.late_fee > 0.0\nRETURN l.loanid AS loan, b.title AS title,\n       i.late_fee AS fee') + '''
<p>The filter keeps only connections with a positive late fee. It reads <code>i.late_fee</code> because the fee belongs to the borrowing edge. A condition on <code>b.late_fee</code> would look for a property on a different element.</p>
<h2>4. Check the result against the data</h2>
<p>In the book's initial instance, loan <code>L-2025-0001</code> includes two books. The edge to <em>Graph Theory</em> has a fee of <code>2.5</code>, while the edge to <em>Graph DB 101</em> has a fee of <code>0.0</code>. The filtered query therefore returns the former connection. Later updates to the sample graph can change this result.</p>
<h2>5. Continue learning</h2>
<p>Try changing the fee threshold and explain which rows survive. Then use <a href="gql-examples.html">the query examples</a> to practice ordering and aggregation. For the complete graph type, sample insertion and update statements, return to <a href="04-gql-by-example.html">GQL by Example</a>. The <a href="07-patterns-and-matching.html">matching chapter</a> explains how patterns produce binding tables.</p>
''')

guide('gql-examples', 'GQL Query Examples: Filters, Ordering and Aggregation',
      'Explore GQL queries over a library graph, with explanations of edge filters, sorting and grouped late-fee totals and links to the full dataset.', '''
<p>These examples use the populated <code>libraryGraph</code> from <a href="04-gql-by-example.html">GQL by Example</a>. Each query answers a different question about loans and books. Begin with the <a href="gql-tutorial.html">tutorial</a> if the pattern notation is new to you.</p>
<h2>Which borrowed books have a late fee?</h2>
''' + code('USE libraryGraph\nMATCH (l:Loan)-[i:INCLUDES]->(b:Book)\nWHERE i.late_fee > 0.0\nRETURN l.loanid AS loan, b.title AS title,\n       i.late_fee AS fee') + '''
<p>The condition applies to an edge property. A book can appear in several loans, each with its own fee. Returning the loan identifier alongside the title keeps those borrowings distinguishable.</p>
<h2>Which due dates come first?</h2>
''' + code("USE libraryGraph\nMATCH (l:Loan)-[i:INCLUDES]->(b:Book)\nRETURN l.loanid AS loan, b.isbn AS isbn,\n       b.title AS title, i.due_date AS due_date\nORDER BY due_date, loan, isbn") + '''
<p>The first sort key is the due date. The loan and ISBN columns break ties between different loan-book pairs in the sample. Without an explicit ordering, a result table should not be treated as a sorted sequence. Read <a href="13-ordering-and-pagination.html">Ordering and Pagination</a> before adding a row limit.</p>
<h2>What is the total late fee for each author?</h2>
''' + code('USE libraryGraph\nMATCH (l:Loan)-[i:INCLUDES]->(b:Book)\nLET authorName = b.author\nRETURN authorName AS author, SUM(i.late_fee) AS total_late_fee\nGROUP BY author\nORDER BY total_late_fee DESC\nLIMIT 10') + '''
<p>This example from Chapter 4 groups matched borrowings by author and sums their edge fees. The amount measures fees across loan-book connections, rather than the number of distinct books. If a more complex pattern produces additional matches for the same connection, check that multiplicity before summing.</p>
<h2>How to adapt an example</h2>
<p>Check the graph's labels, edge direction and property names first. Then verify the database's supported syntax, including grouping and graph selection. The book explains <a href="12-grouping-and-aggregation.html">aggregation semantics</a> and provides <a href="14-data-modification.html">update examples</a> separately, so you can understand reads before changing the dataset.</p>
''')

guide('gql-vs-sql', 'GQL vs SQL: Graph Patterns and Relational Joins',
      'Compare GQL graph patterns with SQL joins using the same loan-and-book question. Understand the data model, result rows and practical tradeoffs.', '''
<p>SQL queries tables; GQL queries property graphs. Both can return tabular results, filter rows and aggregate values. The difference is visible when a query follows connections between entities.</p>
<h2>The same question in two models</h2>
<p>Suppose we need book titles for a particular loan. In a graph, an <code>INCLUDES</code> edge links the loan directly to each book:</p>
''' + code("MATCH (l:Loan)-[:INCLUDES]->(b:Book)\nWHERE l.loanid = 'L-2025-0001'\nRETURN b.title AS title") + '''
<p>A relational design could store loans, books and an association table. With tables <code>loans(loanid)</code>, <code>books(isbn, title)</code> and <code>loan_books(loanid, isbn)</code>, the equivalent question uses joins:</p>
''' + code("SELECT b.title AS title\nFROM loans AS l\nJOIN loan_books AS lb ON lb.loanid = l.loanid\nJOIN books AS b ON b.isbn = lb.isbn\nWHERE l.loanid = 'L-2025-0001'", 'SQL') + '''
<p>The correspondence assumes that these tables encode the same connections as the graph and that the identifiers are unique. Duplicate association rows or different constraints can change result multiplicity.</p>
<h2>Where does relationship data live?</h2>
<p>A due date for a borrowed book belongs on the graph's <code>INCLUDES</code> edge. In the relational design, it belongs in <code>loan_books</code>. The models can represent the same facts, while their query notation exposes those facts differently.</p>
<h2>Patterns still produce rows</h2>
<p>Matching a graph does not imply returning a single graph object. A GQL pattern binds variables into rows, which later operations can filter, combine or aggregate. SQL experience with joins and grouping is useful, but graph path modes and matching rules need separate attention.</p>
<h2>Choosing an approach</h2>
<p>A relationship-heavy question may be easier to express as a graph pattern. A table-oriented workload may fit an existing relational schema well. Query length alone does not establish performance; the data, indexes and execution engine determine the cost.</p>
<p>Read <a href="03-positioning.html">the book's comparison with SQL and other languages</a>, then study <a href="09-algebra-of-binding-tables.html">binding-table algebra</a> and <a href="10-path-semantics.html">path semantics</a> for the formal differences.</p>
''')

guide('gql-vs-cypher', 'GQL vs Cypher: Shared Syntax and Compatibility',
      'Understand how GQL relates to Cypher, what their shared MATCH syntax means and how to check feature compatibility before moving graph queries.', '''
<p>GQL is an ISO database language standard. Cypher is a graph query language used by Neo4j and other implementations. Their familiar pattern notation makes many simple queries look alike, but similar syntax does not establish complete compatibility.</p>
<h2>A familiar query shape</h2>
''' + code("MATCH (l:Loan)-[:INCLUDES]->(b:Book)\nWHERE l.loanid = 'L-2025-0001'\nRETURN b.title AS title") + '''
<p>This pattern binds loans to books along outgoing <code>INCLUDES</code> edges. It uses the <code>MATCH</code>, <code>WHERE</code> and <code>RETURN</code> structure familiar from Cypher. It assumes an appropriate graph context and the library data from <a href="04-gql-by-example.html">Chapter 4</a>.</p>
<h2>What should you check before migration?</h2>
<p>Start with the target database and version. Consult its conformance documentation for the features the query uses. Then inspect graph selection, property types, path restrictions, aggregation and data modification. A graph type definition requires a separate check from a simple read query.</p>
<p>Neo4j's <a href="https://neo4j.com/docs/cypher-manual/current/appendix/gql-conformance/">GQL conformance documentation</a> distinguishes supported features, unsupported mandatory features, optional features with Cypher equivalents and additional Cypher features. Use that documentation for version-specific compatibility.</p>
<h2>Syntax is only part of the comparison</h2>
<p>Two accepted queries can still differ in edge cases. Test empty inputs, missing properties, duplicate matches and repeated paths. Compare the result values and multiplicities, and use explicit ordering when the output order matters. The book's chapters on <a href="08-expressions-and-evaluation.html">expressions and NULL</a> and <a href="10-path-semantics.html">path semantics</a> explain why those cases matter.</p>
<h2>Learning GQL with Cypher experience</h2>
<p>Begin with <a href="gql-examples.html">read queries</a>, then examine <a href="15-types-and-schemas.html">types and schemas</a> and <a href="14-data-modification.html">data modification</a>. Treat vendor extensions as explicit dependencies when portability is a requirement. The <a href="gql-iso-39075.html">standard guide</a> explains the scope of ISO/IEC 39075 and how to use the book alongside it.</p>
''')

guide('gql-iso-39075', 'ISO/IEC 39075: The GQL Standard Explained',
      'Understand the scope of ISO/IEC 39075:2024, the Graph Query Language standard, and find a reading route through GQL syntax, types and semantics.', '''
<p>ISO/IEC 39075:2024 is the international standard for Graph Query Language. Its formal title is <em>Information technology: Database languages: GQL</em>. The first edition was published in April 2024.</p>
<h2>What does the standard specify?</h2>
<p>The specification covers the structures of property graphs and operations for creating, querying, maintaining and controlling graph data. It defines both syntax and semantics: how statements are written and what they mean. See the <a href="https://www.iso.org/standard/76120.html">ISO catalogue record</a> for the publication, preview and related corrections.</p>
<h2>How the book helps you read it</h2>
<p>GQL Essentials combines a library example with a mathematical account of the data model and query evaluation. Start with <a href="04-gql-by-example.html">the concrete example</a>, then read <a href="06-data-model.html">Data Model</a> to connect nodes, edges and properties to formal definitions.</p>
<p>Continue to <a href="07-patterns-and-matching.html">Patterns and Matching</a> for bindings and matching, and <a href="09-algebra-of-binding-tables.html">Algebra of Binding Tables</a> for query composition. These explain the mechanics behind a query result rather than only its notation.</p>
<h2>What about schemas and updates?</h2>
<p>Read <a href="15-types-and-schemas.html">Types and Schemas</a> for graph structure and <a href="14-data-modification.html">Data Modification</a> for updates. The chapters on transactions, authorization and diagnostics develop the book's formal treatment of execution behavior. Proposed extensions are discussed separately in <a href="22-future-enhancements.html">Future Enhancements</a>.</p>
<h2>Using a standard with a real database</h2>
<p>A standard is a specification, while a database implements a particular set of features. Before running examples, check the implementation's conformance statement and feature documentation. Record the database version when comparing behavior. The book is an independent educational text; use the ISO publication for normative requirements.</p>
<p>For a shorter introduction, read <a href="what-is-gql.html">What is GQL?</a> or follow <a href="gql-tutorial.html">the beginner tutorial</a>. The <a href="bibliography.html">bibliography</a> collects the standards and research cited in the book.</p>
''')

def guide_links():
    return '<section id="learn-gql" aria-labelledby="learn-gql-title"><h2 id="learn-gql-title">Learn GQL</h2><p>Start with a short guide, then follow links to the relevant chapters.</p><ul>' + ''.join('<li><a href="' + n + '">' + html.escape(META[n][0]) + '</a></li>' for n in GUIDES) + '</ul></section>'

def update_home_section(source, section_id, markup):
    # These generated sections contain no nested sections. Replace only their
    # markup so the rest of the homepage and converted book stay untouched.
    section = re.compile(r'<section\b(?=[^>]*\bid=["\']' + re.escape(section_id) + r'["\'])[^>]*>.*?</section>', re.S)
    if section.search(source):
        return section.sub(lambda match: markup, source, count=1)
    citation = re.compile(r'<section\b(?=[^>]*\bid=["\']cite-book["\'])[^>]*>')
    if not citation.search(source):
        raise ValueError('Cannot place homepage SEO section: missing #cite-book')
    return citation.sub(lambda match: markup + match[0], source, count=1)

def robots_tags(soup):
    return soup.head.find_all('meta', attrs={'name': re.compile(r'^(robots|googlebot|bingbot)$', re.I)})

def is_indexable(soup):
    return not any(
        {'noindex', 'none'} & set(re.split(r'[\s,]+', tag.get('content', '').lower()))
        for tag in robots_tags(soup)
    )

def apply(site=SITE):
    home = update_home_cover((site / 'index.html').read_text())
    intro = '''<section id="what-is-gql" aria-labelledby="what-is-gql-title"><h2 id="what-is-gql-title">What is GQL (Graph Query Language)?</h2><p>GQL is the international standard ISO/IEC 39075:2024 for querying and managing property graph databases. It defines a language for graph pattern matching, data modification and graph structure definitions.</p><p>This free online book by Dominik Tomaszuk is intended for developers, database professionals, students and researchers. Read it chapter by chapter or use the guides below to explore a specific question.</p></section>'''
    home = update_home_section(home, 'what-is-gql', intro)
    home = update_home_section(home, 'learn-gql', guide_links())
    # Generate guides from the current shell so navigation, search and PDF links stay consistent.
    for filename, body in GUIDES.items():
        soup = BeautifulSoup(home, 'html.parser')
        # Indexing belongs to the individual page, not to the shared homepage shell.
        for tag in robots_tags(soup):
            tag.decompose()
        guide_path = site / filename
        if guide_path.exists():
            existing = BeautifulSoup(guide_path.read_text(), 'html.parser')
            for tag in robots_tags(existing):
                soup.head.append(tag)
        article = soup.select_one('article')
        article.clear()
        article.append(BeautifulSoup('<p class="eyebrow">GQL learning guide · Dominik Tomaszuk</p><h1>' + META[filename][0] + '</h1>' + body + guide_links(), 'html.parser'))
        for tag in soup.select('[aria-current="page"]'):
            del tag['aria-current']
        soup.select_one('.topbar-title').string = 'GQL Essentials / ' + META[filename][0]
        soup.select_one('.layout')['class'] = ['layout']
        (site / filename).write_text(str(soup))
    (site / 'index.html').write_text(home)
    for path in sorted(site.glob('*.html')):
        source = path.read_text()
        if 'href="index.html#learn-gql"' not in source:
            source = source.replace('</nav><div class="sidebar-footer">', '<a class="nav-link" href="index.html#learn-gql">Learn GQL: guides and examples</a></nav><div class="sidebar-footer">', 1)
        soup = BeautifulSoup(source, 'html.parser')
        if path.name in META:
            title, description = META[path.name]
        else:
            heading = soup.h1.get_text(' ', strip=True)
            title = 'GQL ' + heading
            links = [a.get_text(' ', strip=True) for a in soup.select('article .contents-section a')]
            description = 'Read the ' + heading + ' part of GQL Essentials, with chapters on ' + ', '.join(links) + '.'
        if path.name != 'index.html' and 'GQL Essentials' not in title:
            title += ' | GQL Essentials'
        url = BASE + ('' if path.name == 'index.html' else path.name)
        tags = [
            '<meta name="description" content="' + html.escape(description, quote=True) + '">',
            '<title>' + html.escape(title) + '</title>',
            '<link rel="canonical" href="' + url + '">',
        ]
        properties = {'og:type': 'book' if path.name == 'index.html' else 'website', 'og:site_name': 'GQL Essentials', 'og:title': title, 'og:description': description, 'og:url': url, 'og:image': BASE + 'assets/cover.png', 'og:image:alt': 'GQL Essentials by Dominik Tomaszuk, book cover'}
        tags += ['<meta property="' + k + '" content="' + html.escape(v, quote=True) + '">' for k, v in properties.items()]
        tags += ['<meta name="twitter:card" content="summary_large_image">']
        if path.name.startswith('footnote-') and not any(
            tag.get('name', '').lower() == 'robots'
            and {'noindex', 'none'} & set(re.split(r'[\s,]+', tag.get('content', '').lower()))
            for tag in robots_tags(soup)
        ):
            tags += ['<meta name="robots" content="noindex,follow">']
        if path.name == 'index.html':
            book = {'@context': 'https://schema.org', '@type': 'Book', '@id': BASE + '#book', 'name': 'GQL Essentials', 'author': {'@type': 'Person', 'name': 'Dominik Tomaszuk', 'sameAs': 'https://orcid.org/0000-0003-1806-067X'}, 'publisher': {'@type': 'Organization', 'name': 'Wydawnictwo Uniwersytetu w Białymstoku'}, 'datePublished': '2026', 'isbn': '978-83-7431-884-6', 'identifier': 'https://doi.org/10.15290/GQL_Essentials_2026', 'inLanguage': 'en', 'bookFormat': 'https://schema.org/EBook', 'isAccessibleForFree': True, 'url': BASE, 'image': BASE + 'assets/cover.png', 'description': 'A book introducing Graph Query Language (GQL), ISO/IEC 39075, its syntax, data model and formal semantics.'}
            tags += ['<script type="application/ld+json">' + json.dumps(book, ensure_ascii=False) + '</script>']
        # Replace only head metadata, leaving converted chapter text and MathML byte-for-byte intact.
        head_match = re.search(r'<head>(.*?)</head>', source, re.S)
        head = head_match[1]
        head = re.sub(r'<title>.*?</title>|<link\b[^>]*rel="canonical"[^>]*>|<meta\b[^>]*(?:name="(?:description|twitter:[^"]*)"|property="og:[^"]*")[^>]*>|<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
        head = re.sub(r'\n\s*\n', '\n', head)
        source = source[:head_match.start(1)] + head.rstrip() + '\n' + '\n'.join(tags) + source[head_match.end(1):]
        path.write_text(source)
    search_path = site / 'assets/search-index.js'
    search = json.loads(search_path.read_text().removeprefix('window.BOOK_SEARCH = ').strip().removesuffix(';'))
    search = [entry for entry in search if entry['url'].split('#')[0] not in GUIDES]
    for filename, body in GUIDES.items():
        search.append({'title': META[filename][0], 'url': filename, 'text': BeautifulSoup(body, 'html.parser').get_text(' ', strip=True)})
    search_path.write_text('window.BOOK_SEARCH = ' + json.dumps(search, ensure_ascii=False).replace('</', '<\\/') + ';\n')
    # Only include pages that permit indexing. The detailed contents page is
    # distinct from the homepage and keeps its own canonical URL.
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    root = ET.Element('{' + namespace + '}urlset')
    for path in sorted(site.glob('*.html')):
        if not is_indexable(BeautifulSoup(path.read_text(), 'html.parser')):
            continue
        entry = ET.SubElement(root, '{' + namespace + '}url')
        ET.SubElement(entry, '{' + namespace + '}loc').text = BASE + ('' if path.name == 'index.html' else path.name)
    ET.indent(root)
    ET.ElementTree(root).write(site / 'sitemap.xml', encoding='UTF-8', xml_declaration=True)

if __name__ == '__main__':
    apply()
