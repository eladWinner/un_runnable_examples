public class DynamicGraph {
    //private GraphEdge E ;not used just adds complication while using adjlist format
    public GraphNode V ;
    public DynamicGraph(){}
    //O(1)
    public GraphNode insertNode(int nodeKey){
        if (V==null)
            V= new GraphNode(nodeKey);
        else {
            GraphNode temp = new GraphNode(nodeKey);
            temp.addNext(V);
            V=temp;
        }
        return V;
    }
    public void deleteNode(GraphNode node) {
        if ( (node.adjout == null) && ( node.adjin == null)){
            if(node.previous!=null)
                node.previous.next=node.next;
            else // means node is first in V
                V=node.next;
        }
    }
    //O(1)
    public GraphEdge insertEdge(GraphNode from, GraphNode to){
        return new GraphEdge(from ,to); // all internally manged
    }
    public void deleteEdge(GraphEdge edge){
        edge.removeEdge();
    }


    private void DFSbuildCopy_visit(GraphNode at ,GraphNode root){
        //System.out.println(at.getKey()+"at a dfsB copy"+root.getKey());
        GraphEdge backwardsCon =at.adjin;
        GraphNode copynode = new GraphNode(at.getKey());
        insertEdge(root,copynode);
        //insertEdge(root,copynode);
        while (backwardsCon!=null) {
            if (backwardsCon.from.flag1 == false) {

                backwardsCon.from.flag1 = true;
                DFSbuildCopy_visit(backwardsCon.from,copynode);
            }
            backwardsCon = backwardsCon.next;
        }

    }
    private void DFSDecrisingOrder(GraphNode at, list<GraphNode> decs){
        //instead of a list will have an empty node with connections to every node in order i want
        GraphEdge conn = at.adjout;
        while (conn!=null){
            if (conn.to.flag1==false){
                conn.to.flag1=true;
                DFSDecrisingOrder(conn.to,decs);
            }
            conn=conn.next;
        }

        decs.push(new linkedList<>(at));
    }
    public RootedTree scc(){
        RootedTree theTree = new RootedTree();
        theTree.starttree();
        //intailazie for DFS
        GraphNode at = V ;
        while ( at!=null){ at.flag1= false; at=at.next;} // marks all nodes as unvisted
        list<GraphNode> stackDescendingF =new list<>(new linkedList<>(theTree.root));
        at= V;
        while (at!=null) {
            if (at.flag1==false ){
                at.flag1=true;
                DFSDecrisingOrder(at,stackDescendingF);
            }
            at=at.next;
        }
        //removing last , that was used to initialize
        stackDescendingF.last.prev.next=null;
        stackDescendingF.last=stackDescendingF.last.prev;
        //: "ψ = the sequence of vertices v ∈ V in order of decreasing v.f ".
        //3: construct the transpose digraph ←−G of G
        // 4: run DFS(←−G ), processing the vertices in line 5 in ψ-order and
        // 5: output the vertices of each tree in the DFS forest as a SCC
        at = V ;
        while ( at!=null){ at.flag1= false; at=at.next;} // marks all nodes as unvisted
        do {
            if (stackDescendingF.currentValue().flag1==false){
                stackDescendingF.currentValue().flag1=true;
                DFSbuildCopy_visit(stackDescendingF.currentValue(),theTree.root);
            }
        }while (stackDescendingF.goNext());
        return theTree;
    }
    public RootedTree bfs(GraphNode source){
        DynamicGraph tempo =new DynamicGraph();
        RootedTree theTree = new RootedTree();
        theTree.setRoot(tempo.insertNode(source.getKey())); //creates a new graph that is a tree
        GraphNode at = V; // mark all nodes in G as unvisted
        while (at!=null){at.flag1=false; at=at.next;}
        source.flag1=true;
        //unneed complication . i want to not implement a linkedlist / stack / other out side data structure .
        //so ill use the trick of a virtual node connected to the list /stack.
        list<GraphNode> Enqueue =new list<>(new linkedList<>(source));
        list<GraphNode> mirrorEnqueue =new list<>(new linkedList<>(theTree.root));

        //currently Enqueue has only 1 connection

        do{
            GraphNode U =Enqueue.currentValue();
            GraphNode mirrorU =mirrorEnqueue.currentValue();
            GraphEdge at2 = U.adjout ;
            while (at2!=null){
                if (at2.to.flag1==false) {//meaning this node was not visted
                    at2.to.flag1=true;
                    GraphNode mirrorNode =new GraphNode(at2.to.getKey());
                    insertEdge(mirrorU,mirrorNode); // adds a copy of the connection BFS traveled in
                    Enqueue.addtoEnd(new linkedList<>(at2.to));
                    mirrorEnqueue.addtoEnd(new linkedList<>(mirrorNode));
                }
                at2=at2.next;
            }
            mirrorEnqueue.currentValue().flag1=true;
            mirrorEnqueue.goNext();
        }while (Enqueue.goNext());
        return theTree;
    }
}
