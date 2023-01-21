import java.io.DataOutputStream;
import java.io.IOException;

import static java.lang.System.out;



public class main1
{
    public static void main(String[] args) throws IOException
    {

        DataOutputStream outStream = new DataOutputStream(out);
        DynamicGraph DG = new DynamicGraph();
        RootedTree rootedTree ;
        GraphNode g1 = DG.insertNode(1);
        GraphNode g2 =DG.insertNode(2);
        GraphNode g3 = DG.insertNode(3);
        GraphNode g4 = DG.insertNode(4);
        GraphNode g5 = DG.insertNode(5);
        GraphNode g6 = DG.insertNode(6);
        GraphNode g7 = DG.insertNode(7);


        DG.insertEdge(g7,g6);
        DG.insertEdge(g6,g5);
        DG.insertEdge(g6,g1);
        DG.insertEdge(g5,g7);
        DG.insertEdge(g5,g6);
        DG.insertEdge(g5,g4);
        DG.insertEdge(g4,g3);
        DG.insertEdge(g3,g4);
        rootedTree=DG.bfs(g7);
        rootedTree=DG.scc();
        outStream.writeBytes("Print in Preorder after SCC:" + System.lineSeparator());
        rootedTree.preorderPrint(outStream);
        outStream.writeBytes(System.lineSeparator());
        outStream.writeBytes("layers print after SCC:" + System.lineSeparator());
        rootedTree.printByLayer(outStream);
        //Random random = new Random();
        // fix the seed to reproduce the run
        //random.setSeed(Constants.SEED);
        //testDynamicGraph(random);
    }

}