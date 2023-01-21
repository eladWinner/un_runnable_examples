public class GraphNode {
    public int nodesValue;
    public GraphEdge adjout =null , adjin=null;
    public GraphNode next =null , previous= null; // for V
    public boolean flag1 ,flag2; // auxiliary info , to help other functions

    public GraphNode(int number){nodesValue=number;}
    public int getKey(){return nodesValue;}
    public int getOutDegree(){
        GraphEdge at =adjout ; int count =0;
        while (at!=null){ count++; at=at.next;}
        return count;
    }
    public int getInDegree(){
        GraphEdge at =adjin ; int count =0;
        while (at!=null){ count++; at=at.next;}
        return count;
    }


    public  void addNext( GraphNode other){ next=other;other.previous=this;}
}
