using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using static System.Console;
using System.Text.Json;
using Newtonsoft.Json;
using System.Runtime.CompilerServices;
using Microsoft.CodeAnalysis.CSharp.Syntax;

public class fileClass
{
    public string sample_repo_name { get; set; }
    public string sample_path { get; set; }
    public string content { get; set; }
}

public class simpleLeafNode
{
    public string type { get; set; }
}

public class valueLeafNode
{
    public string type { get; set; }
    public string value { get; set; }
    public string parentType { get; set; }
    public string SymbolType { get; set; }
}

public class simpleNode
{
    public string type { get; set; }
    public int[] children { get; set; }
}

public class valueNode
{
    public string type { get; set; }
    public int[] children { get; set; }
    public string value { get; set; }
    public string parentType { get; set; }
    public string SymbolType { get; set; }
}




class Program
{

    private int failedReads = 0;


    private static string write(List<SyntaxNodeOrToken> ordered, SemanticModel model)
    {
        //string line = "[";
        List<Object> nodes = new List<Object>();
        foreach (SyntaxNodeOrToken nort in ordered)
        {
            string type = nort.Kind().ToString();
            List<int> children = new List<int>();
            if (nort.ChildNodesAndTokens().Count != 0)
            {
                foreach (SyntaxNodeOrToken child in nort.ChildNodesAndTokens())
                {
                    children.Add(ordered.FindLastIndex(child.Equals));
                }

            }
            string value = null;
            string parentType = null;
            string symbolTypeString = "null";
            if (nort.IsKind(SyntaxKind.IdentifierToken))
            {
                value = nort.AsToken().ValueText;

                if (nort.IsKind(SyntaxKind.IdentifierToken))
                {
                    SyntaxKind par = nort.Parent.Kind();
                    var symbolType = model.GetSymbolInfo(nort.Parent).Symbol;
                    if (par == SyntaxKind.IdentifierName)
                    {
                        par = nort.Parent.Parent.Kind();
                    }
                    parentType = par.ToString();
                    if (symbolType != null)
                    {
                        string symbolTypeName = symbolType.GetType().ToString();
                        symbolTypeString = symbolTypeName;
                    }
                    else
                    {
                        var secSymbolType = model.GetSymbolInfo(nort.Parent).CandidateSymbols;
                        if (!secSymbolType.IsEmpty)
                        {
                            symbolTypeString = secSymbolType[0].GetType().ToString();
                        }
                        else
                        {
                            
                            //Console.WriteLine("symbol is null: " + dnort);
                            //Console.WriteLine(nort.Parent + "\n\n");
                            symbolTypeString = "null";
                        }
                    }
                }
            }
            if (symbolTypeString == "null" && parentType != null)
            {
                if (parentType.Contains("Declarat")) symbolTypeString = "Declaration";
                if (parentType.Contains("Creation")) symbolTypeString = "Creation";
                if (parentType.Contains("Parameter")) symbolTypeString = "Parameter";
                if (parentType.Contains("QualifiedName") || parentType == "SimpleMemberAccessExpression")
                {
                    var parent = nort.Parent.Parent;
                    while (parent.Kind().ToString() == "QualifiedName" || parent.Kind().ToString() == "SimpleMemberAccessExpression")
                    {
                        parent = parent.Parent;
                    }
                    parentType += "-" + parent.Kind();

                }
            }
            
            if (children.Count == 0)
            {
                if (value == null)
                {
                    nodes.Add(new simpleLeafNode() { type = type });
                }
                else
                {
                    nodes.Add(new valueLeafNode() { type = type, value = value, parentType = parentType, SymbolType = symbolTypeString });
                }
            }
            else
            {
                if (value == null)
                {
                    nodes.Add(new simpleNode() { type = type, children = children.ToArray() });
                }
                else
                {
                    nodes.Add(new valueNode() { type = type, value = value, parentType = parentType, SymbolType = symbolTypeString, children = children.ToArray() });
                }
            }
        }


        return System.Text.Json.JsonSerializer.Serialize(nodes);
    }

    static List<SyntaxNodeOrToken> inOrder(SyntaxNodeOrToken root)
    {
        List<SyntaxNodeOrToken> tree = new List<SyntaxNodeOrToken>();
        tree.Add(root);
        foreach (SyntaxNodeOrToken child in root.ChildNodesAndTokens())
        {
            List<SyntaxNodeOrToken> subtree = inOrder(child);
            foreach (SyntaxNodeOrToken c in subtree)
            {
                tree.Add(c);
            }
        }
        return tree;
    }



    public static void Write(List<SyntaxReference> ssts, List<MetadataReference> refs, StreamWriter w)
    {
        ReaderWriterLockSlim rwl = new ReaderWriterLockSlim();


        var trustedAssembliesPaths = ((string)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES")).Split(Path.PathSeparator);

        foreach (var trusted in trustedAssembliesPaths)
        {
            refs.Add(MetadataReference.CreateFromFile(trusted));
        }

        MetadataReference[] references = refs.ToArray();

        //Console.WriteLine("number of references is: " + refs.Count());
        CSharpCompilation compilation;

        {
            List<SyntaxTree> trees = new List<SyntaxTree>();
            foreach (var r in ssts) trees.Add(r.SyntaxTree);

            compilation = CSharpCompilation.Create("NamedAssembly", trees, references);
        }

        parrallelWriter(compilation, w, rwl);

    }

    //method completely written by CoPilot
    private static void parrallelWriter(CSharpCompilation compilation, StreamWriter w, ReaderWriterLockSlim rwl)
    {
        Console.WriteLine("Am in parallel writer with " + compilation.SyntaxTrees.Length + " trees");
        Parallel.ForEach(compilation.SyntaxTrees, tree =>
        //foreach(var tree in compilation.SyntaxTrees)
        {
            try
            {
                var model = compilation.GetSemanticModel(tree);
                var ordered = inOrder(tree.GetRoot());

                var line = write(ordered, model);
                if (line == "[]") WriteLine("line is empty: \n" + tree.ToString());

                rwl.EnterWriteLock();
                w.Write(line + "\n");
                rwl.ExitWriteLock();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.GetType + ": failed to write line");
            }
            
        });
    }


    /*public (List<SyntaxTree>, List<MetadataReference>) parallelRead(String dir)
    {
        ReaderWriterLockSlim rwl = new ReaderWriterLockSlim();
        List<SyntaxTree> ssts = new List<SyntaxTree>();
        List<MetadataReference> refs = new List<MetadataReference>();
        foreach (var subdir in Directory.GetDirectories(dir))
        {
            var (trees, references) = parallelRead(subdir);
            foreach (var t in trees)
            {
                ssts.Add(t);

            }

            foreach (var r in references)
            {
                refs.Add(r);
            }

        }
        foreach (var subfile in Directory.GetFiles(dir))
        {
            if (Path.GetExtension((string)subfile) == ".cs")
            {
                var t = Reader(subfile, rwl);
                if (t != null) ssts.Add(t);
                refs.Add(MetadataReference.CreateFromFile(subfile));
            }
            if (Path.GetExtension((string)subfile) == ".dll")
            {
                refs.Add(MetadataReference.CreateFromFile(subfile));
            }
        }

        Console.WriteLine("read is returning " + ssts.Count() + " ssts");
        return (ssts, refs);
    }*/


    private List<SyntaxReference> Reader(String line)
    {
        
        ///List<fileClass> classes = new List<fileClass>();

        var classes = JsonConvert.DeserializeObject<fileClass[]>(line);

        List<SyntaxReference> syntaxTreeList = new List<SyntaxReference>();

        foreach (var c in classes)
        {
            var tree = CSharpSyntaxTree.ParseText(c.content);
            syntaxTreeList.Add(tree.GetRoot().GetReference());
        }
        
        return syntaxTreeList;
    }


    static void Main(string[] args)
    {
        const string file_in = "C:\\Users\\milan\\Desktop\\Ds\\outputEdit.json";
        const string file_out = "C:\\Users\\milan\\Desktop\\realAsts.json";
        const string file_out2 = "C:\\Users\\milan\\Desktop\\errors.json";
        try
        {
            FileStream fs = File.Create(file_out);
            fs.Close();
            FileStream fs2 = File.Create(file_out2);
            fs2.Close();
        }
        catch (Exception e)
        {
            WriteLine(e);
            throw;
        }

        StreamWriter w = new StreamWriter(file_out);
        StreamWriter w2 = new StreamWriter(file_out2);
        Program prog = new Program();
        List<MetadataReference> refs = new List<MetadataReference>();

        StreamReader sr = new StreamReader(file_in);
        var line = sr.ReadLine();
        int faileds = 0;
        while (line != null)
        {
            
            var s = prog.Reader(line);
            Console.WriteLine("length of ssts is: " + s.Count());
            try
            {
                Program.Write(s, new List<MetadataReference>(), w);
            }               
            catch (Exception e)
            {
                WriteLine("failed to write " + ++faileds +" lines");
                w2.WriteLine(e);
            }

            line = sr.ReadLine();
            
        }
        WriteLine("Finished program wrote all lines except for: " + faileds);
        
        w.Close();
    }

}

