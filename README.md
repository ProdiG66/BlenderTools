# Blender Tools

A collection of handy Blender add-ons designed to streamline common workflows, especially for game asset preparation and organization. This repository includes tools for automatic Level of Detail (LOD) generation, bulk renaming, and optimized FBX export for Unity.

---

## 🧰 Included Tools

### 1. LOD Generator
Generate LOD (Level of Detail) meshes using the Decimate modifier.

### 2. Name Replacer
Batch rename objects, bones, materials, and textures with configurable prefix/suffix options.

### 3. Unity Exporter
Export selected Blender objects to Unity-ready FBX files, with built-in validation and texture packing support.

---

## 🔧 Installation

### 🔁 Clone the Repository

```bash
git clone https://github.com/ProdiG66/BlenderTools.git
```

1. Open Blender.
2. Go to `Edit > Preferences > Add-ons`.
3. Click `Install...` and select the `.py` script you want to install from this repo.
4. Enable the checkbox to activate the add-on.
5. The tools will appear in the **3D Viewport > Sidebar > Tools tab**.

---

## 🌀 LOD Generator

### 📌 Features
- Generate multiple LODs from selected mesh objects.
- Choose between `Collapse` and `Unsubdivide` modes.
- Control LOD count and reduction amount.

### 🚀 How to Use
1. Select one or more mesh objects in the scene.
2. Open the **Tools** tab in the sidebar.
3. In the **LOD Generator** panel:
    - Set the number of LODs (1–10).
    - Choose a Decimate Type:
        - **Collapse**: ratio-based reduction.
        - **Unsubdivide**: edge simplification.
    - Adjust `Decimate Step` if using Collapse.
4. Click **Generate LODs**.

### 📂 Output
- Creates duplicated versions named `ObjectName_LOD1`, `LOD2`, etc.
- Applies appropriate decimation per level.

---

## ✍️ Name Replacer

### 📌 Features
- Replace prefix or suffix in object, bone, material, or texture names.
- Supports four modes:
    - `Prefix → Prefix`
    - `Prefix → Suffix`
    - `Suffix → Prefix`
    - `Suffix → Suffix`

### 🚀 How to Use
1. Open the **Tools** tab.
2. In the **Name Replacer** panel:
    - Enter the **Old String** and **New String**.
    - Select the **Replace Mode** and **Target Type** (Objects, Bones, Materials, Textures).
3. Click **Replace String**.

### 💡 Example
| Input | Mode | Result |
|-------|------|--------|
| `Char_A`, `Char_B` | Prefix → Prefix (`Char` → `Player`) | `Player_A`, `Player_B` |

---

## 📦 Unity Exporter

### 📌 Features
- Export selected objects as Unity-compatible FBX files.
- Choose to export all at once or individually.
- Optional texture embedding and animation export.
- Built-in validation for names, scale, materials, and texture paths.

### 🚀 How to Use
1. Select visible objects to export.
2. Open the **Tools** tab.
3. In the **Export FBX for Unity** panel:
    - Choose an **Export Path**.
    - Set options:
        - Include animations?
        - Include textures?
        - Export each object separately?
    - If exporting all at once, provide a filename.
4. Click **Export FBX**.

### 🧪 Validation
- Warnings for:
    - Object/mesh name mismatch
    - Unapplied scale
    - Missing materials or textures
- Optional summary display inside the UI.

---

## ▶️ Running From Script

If you're not installing as an add-on, you can run any tool manually:
1. Open Blender's **Scripting** workspace.
2. Paste the full script into a new text editor.
3. Click **Run Script**.

The panels will appear in the **3D Viewport > Sidebar > Tools** tab.

---

## 📁 Repo Structure

```
BlenderTools/
├── Scripts/
│ ├── LODGenerator.py
│ ├── NameReplacer.py
│ └── UnityExporter.py
├── .gitignore
├── LICENSE
└── README.md
```

You can keep the scripts separate or combine them as needed.

---

## 🧠 Notes

- These tools are optimized for Blender 3.0+.
- The Unity Exporter assumes objects are properly UV-unwrapped and scaled (1.0 on all axes) for Unity.
- Always back up your .blend file before batch operations.

---

## 📜 License

MIT License. Free to use, modify, and distribute.

---

## ✉️ Contact

For suggestions or issues, feel free to contact me via email.