import java.io.DataOutputStream;
import java.io.IOException;
public class RootedTree {
    public GraphNode root;
    public RootedTree(){}
    public RootedTree(GraphNode r){root =r;}
    public void setRoot(GraphNode r){root =r;}
    public void starttree(){root=new GraphNode(0);}

    public void printByLayer(DataOutputStream out){
        list<GraphNode> thisLayer =new list<>(new linkedList<>(root));
        GraphEdge atedge = root.adjout;
        list<GraphNode> nextLayer = null;
        boolean atend =false ,didlast=false,firstinlayer =true;
        //do first
        try {out.writeBytes(""+root.getKey());} catch (IOException e) {}
        atedge = root.adjout;
        while (atedge != null) {
            if (nextLayer == null)
                nextLayer = new list<GraphNode>(new linkedList<GraphNode>(atedge.to));
            else
                nextLayer.addtoEnd(new linkedList<>(atedge.to));
            atedge = atedge.next;
        }
        didlast=true;
        //end of first
        while (!atend){
            while (!didlast) {
                GraphNode U = thisLayer.currentValue();
                if (firstinlayer) {
                    firstinlayer = false;
                    try {out.writeBytes(System.lineSeparator() + "" + U.getKey());} catch (IOException e) {}
                } else {
                    try {out.writeBytes("," + U.getKey());} catch (IOException e) {}
                }
                atedge = U.adjout;
                while (atedge != null) {
                    if (nextLayer == null)
                        nextLayer = new list<GraphNode>(new linkedList<GraphNode>(atedge.to));
                    else
                        nextLayer.addtoEnd(new linkedList<>(atedge.to));
                    atedge = atedge.next;
                }
                didlast=thisLayer.isAtEnd();
                thisLayer.goNext();
            }
            firstinlayer=true; didlast=false;
            if (nextLayer ==null)
                atend=true;
            else
            {
                thisLayer=nextLayer;
                nextLayer=null;
            }
        }
        try {out.writeBytes(System.lineSeparator());} catch (IOException e) {}
    }

    private void preorderPrint(DataOutputStream out,boolean isFirst) {
        if (!isFirst)
            try{out.writeBytes(",");} catch (IOException e){}
        try{out.writeBytes(""+root.getKey());} catch (IOException e){}
        RootedTree temporary =new RootedTree();
        GraphEdge outcon = root.adjout;
        while (outcon!=null){
            temporary.setRoot(outcon.to);
            temporary.preorderPrint(out,false);
            outcon=outcon.next;
        }
    }
    public void preorderPrint(DataOutputStream out){
        preorderPrint(out, true);
    }
}
