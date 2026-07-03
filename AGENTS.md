\# Dimension Tools Development Rules



\## Project Goal



Dimension Tools is a CAD-like dimensioning addon for Blender.



The goal is NOT to reproduce Blender Measure Tool.



The goal is to provide SketchUp + AutoCAD style dimensions.



\---



\# General Rules



\- Blender 5.1+

\- Python only

\- GPU overlay only

\- Never create Curve objects for dimensions

\- Never create Mesh objects for dimensions

\- Dimensions are addon data only



\---



\# Scene Data



Only Blender PropertyGroups may be stored in bpy.types.Scene.



Never store:



\- Python objects

\- GPU batches

\- lists

\- dictionaries



Everything else belongs to runtime managers.



\---



\# Rendering



All dimensions are rendered using GPU.



Nothing is stored as geometry.



Renderer is responsible for:



\- extension lines

\- dimension line

\- arrows

\- text



\---



\# Dimension



Dimension stores only logical information.



Dimension never stores geometry.



Dimension contains:



\- id

\- point A

\- point B

\- chain id

\- text override

\- visibility

\- selection



\---



\# Chains



Keep Same Level does not exist.



Instead:



DimensionChain



contains



\- plane

\- offset

\- dimensions



New dimensions automatically join nearby chains.



\---



\# Modal Tool



The operator behaves like Knife Tool.



Activate once.



Create unlimited dimensions.



Exit using ESC.



\---



\# Selection



Dimensions are selectable.



Delete removes only selected dimensions.



\---



\# UI



Global settings only.



Text Size



Arrow Size



Line Width



Color



Units



\---



\# Coding



Prefer composition.



Avoid huge classes.



Each module has one responsibility.



No circular imports.



Every public class has docstrings.



