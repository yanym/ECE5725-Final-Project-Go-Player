#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<math.h>
#include<assert.h>
#include<Python.h>
#include"egolib.h"


#define FREE 0
#define BLACK 1
#define WHITE 2
#define NCHILD 16
#define NDIMENSION 2
#define MAXMOVE 721
#define SAMPLESIZE 727
#define BOARDSIZE 19
#define NOUTPUT 362
#define MAXSTACKSIZE 255
#define MAXNODENUM 65535
#define MAXEDGENUM 1048560
#define ALLZERO {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}



    

const unsigned int sizeofboard=sizeof(int[19][19]);
const int blankboard[19][19]= {[0 ... 18]=ALLZERO};

typedef int MOVE[NDIMENSION];
typedef float NNOUTPUT[362];

//-----------------------
//      Struct: Record
//-----------------------

//Black: -1, None: 0, White: 1
typedef struct record{
    int round;
    int board[BOARDSIZE][BOARDSIZE];
}record_t;

typedef struct prob_distribution{
    int pass_flag; // 0 or 1;
    MOVE move;     // Normal or {19,19}
    double probability;
}pd_t;

typedef struct predict{
    double winrate;
    int nmove;
    pd_t pd[NCHILD];
}predict_t;


//-----------------------
//     Struct: Tree
//-----------------------

//The struct tree_edge is one of the member variable in the struct tree_node.
struct tree_edge;

struct tree_node{
    int npass;
    MOVE *p_move;
    double winrate;
    int nchildren;
    int npredict;
    int total_visit;
    int round; //Count steps, which is also the depth of tree, in the game.
        //Additionally, the round can also be used to determine whose turn it is.
   
    record_t *p_record;
    struct tree_node *p_parent;
    struct tree_edge *p_edge;  //point to the first edge struct in the edge array.
  
};

struct tree_edge{
    int pass_flag;
    MOVE move;
    int nvisit;
    double probability;
    struct tree_node* p_child;
};

typedef struct tree_node node_t;
typedef struct tree_edge edge_t;

//-----------------------
//      Struct: Repo
//-----------------------
typedef struct node_repo{
    node_t *p_item;
    int index;
}node_repo_t;

typedef struct edge_repo{
    edge_t *p_item;
    int index;
}edge_repo_t;

typedef struct record_repo{
    record_t *p_item;
    int index;
}record_repo_t;


typedef struct repo_list{
    node_repo_t* sp_node_repo;
    edge_repo_t* sp_edge_repo;
    record_repo_t* sp_record_repo;
    
}repo_t;


typedef struct ego_stack{
    node_t ** array;
    int index;
    int size;
}estack_t;


//-----------------------
//        Util
//-----------------------


void* util_malloc(int size){
    void* ptr = malloc(size);
    if(ptr == NULL){
        printf("Error raised from memory allocation!\nExit!\n");
        exit(EXIT_FAILURE);
    }
    
    return ptr;
    
}

FILE* util_fopen(char* name, char* access){
    FILE* fp = fopen(name, access);
    
    if(fp == NULL){
        printf("Error raised from file opening.\nExit!\n");
        exit(EXIT_FAILURE);
    }
    
    return fp;
    
}



//-----------------------
//      Tree Node
//-----------------------

node_repo_t *node_repo_init(void){
    node_repo_t *sp;
    sp = (node_repo_t*)util_malloc(sizeof(node_repo_t));
    sp->index = 0;
    sp->p_item = (node_t*)util_malloc((MAXNODENUM+1)*sizeof(node_t));
    return sp;
}

node_t* node_repo_add(node_repo_t* sp){
    if(sp == NULL || sp->index >=MAXNODENUM){
        
        if(sp == NULL){
            printf("EGO: NULL Pointer Exception for sp_node_repo.");
            exit(EXIT_FAILURE);
        }else{
            printf("Node_Repo_Add Error: pointer index overflow!\nIndex restarts from 0!");
            sp->p_item -= sp->index;
            sp->index = 0;
            return sp->p_item;
        }
    }
    
    node_t* p_temp = sp->p_item;
    sp->p_item += 1;
    sp->index += 1;
    return p_temp;
    
}


edge_repo_t *edge_repo_init(void){
    edge_repo_t *sp;
    sp = (edge_repo_t*)util_malloc(sizeof(edge_repo_t));
    sp->index = 0;
    sp->p_item = (edge_t*)util_malloc((MAXEDGENUM +1)*sizeof(edge_t));
    return sp;
}

edge_t* edge_repo_add(edge_repo_t* sp){
    if(sp == NULL || sp->index >=MAXEDGENUM ){
        
        if(sp == NULL){
            printf("EGO: NULL Pointer Exception for sp_edge_repo.");
            exit(EXIT_FAILURE);
        }else{
            printf("Edge_Repo_Add Error: pointer index overflow!\nIndex restarts from 0!");
            sp->p_item -= sp->index;
            sp->index = 0;
            return sp->p_item;
        }
    }
    
    edge_t* p_temp = sp->p_item;
    sp->p_item += NCHILD;
    sp->index += NCHILD;
    return p_temp;
    
}

record_repo_t *record_repo_init(void){
    record_repo_t *sp;
    sp = (record_repo_t*)util_malloc(sizeof(record_repo_t));
    sp->index = 0;
    sp->p_item = (record_t*)util_malloc((MAXNODENUM+1)*sizeof(record_t));
    return sp;
}

record_t* record_repo_add(record_repo_t* sp){
    if(sp == NULL || sp->index >=MAXNODENUM){
        
        if(sp == NULL){
            printf("EGO: NULL Pointer Exception for sp_node_repo.");
            exit(EXIT_FAILURE);
        }else{
            printf("Node_Repo_Add Error: pointer index overflow!\nIndex restarts from 0!");
            sp->p_item -= sp->index;
            sp->index = 0;
            return sp->p_item;
        }
    }
    
    record_t* p_temp = sp->p_item;
    sp->p_item += 1;
    sp->index += 1;
    return p_temp;
    
}

//-----------------------
//    Functions of Repo
//-----------------------

void repo_init(repo_t* p_repo){
    p_repo->sp_node_repo = node_repo_init();
    p_repo->sp_edge_repo = edge_repo_init();
    p_repo->sp_record_repo = record_repo_init();
}

void repo_free(repo_t* p_repo){
    free(p_repo->sp_node_repo);
    free(p_repo->sp_edge_repo);
    free(p_repo->sp_record_repo);
}


estack_t *stack_init(int size){
    estack_t *sp;
    sp = (estack_t*)util_malloc(sizeof(estack_t));
    sp->size = size;
    sp->index = 0;
    sp->array = (node_t**)util_malloc((size+1) * sizeof(node_t*));
    return sp;
}

int is_empty_stack(estack_t* sp){
    if(sp == NULL || sp->index <=0){
        return 1;
    }
    
    return 0;
    
}

int stack_push(estack_t* sp,node_t* p_node){
    if(sp == NULL || sp->index >= sp->size){
        return 0;
    }
    
    sp->array[sp->index++] = p_node;
    return 1;
    
}

int stack_pop(estack_t* sp, node_t** p_node){
    if(sp == NULL || sp->index <=0){
        return 0;
    }
    
    *p_node = sp->array[--sp->index];
    return 1;
    
}


void stack_free(estack_t *sp){
    
    free(sp->array);
    free(sp);
    
}





void edge_init(predict_t *p_predict,edge_t *p_edge){
    
    int nmove = p_predict->nmove;
    assert(nmove <= NCHILD && nmove>0);
    
    int i = 0;
    for(; i < nmove; i++){
        p_edge->pass_flag = p_predict->pd[i].pass_flag;
        p_edge->move[0] = p_predict->pd[i].move[0];
        p_edge->move[1] = p_predict->pd[i].move[1];
        p_edge->nvisit = 0;
        p_edge->probability = p_predict->pd[i].probability;
        p_edge++;
    }
}



double priority_cal(double p, int nvisit, int n_total_visit, int d){
    
    double na = (double) nvisit;
    double ntotal = (double) n_total_visit;
    double result;
    double coef;
    if(d>=0){
        if(d==0){
            double base0 =0.86;
            coef = pow(base0,na);
        }else if(d==1){
            double base1 =0.9;
            coef = pow(base1,na);
        }else if(d==2){
            double base2 =0.95;
            coef = pow(base2,na);
        }else{
            coef =1.0;
        }
        result = coef * p * sqrt(ntotal) / (1.0+na);
    }else{
        result = p ;
    }
    return result;
}

int max_priority(node_t *p_search, double c, int depth){
    /*
     If depth = -1, temperature coef is disabled.
     TODO: "c" is useless now. Remove it further.
     */
    int n = p_search->npredict;
    edge_t *p = p_search->p_edge;
    assert(n<=NCHILD);
    int max_index=0;
    double max_value;
    int i=0;
    for(;i<n;i++){
        double priority = priority_cal(p->probability,p->nvisit,p_search->total_visit, depth);
        if(p->nvisit > 0){
            priority *= pow(p->p_child->winrate+0.5,2);
            
        }
        if(priority > max_value){
             max_index = i;
            max_value = priority;
        }
        p++;
    }
    return max_index;
}

node_t *node_init(repo_t* p_repo){
    
    //TODO: EDGE AND RECORD REPO.
    node_t *p_root = node_repo_add(p_repo->sp_node_repo);
    
    p_root->npass=0;
    p_root->p_move = NULL;
    p_root->winrate = 0.5;
    p_root->nchildren = 0;
    p_root->total_visit = 0;
    p_root->round = 0;
    p_root->p_parent = NULL;
    p_root->round = 0;
    
    record_t newgame;
    p_root->p_record = &newgame;
    newgame.round = 0;
    memcpy(newgame.board,blankboard,sizeofboard);

    predict_t predict_result;
    predict_t *p_predict = &predict_result;
  
    p_root->npredict = p_predict->nmove;
    
    p_root->p_edge = edge_repo_add(p_repo->sp_edge_repo);
    p_root->winrate = p_predict->winrate;
    edge_init(p_predict,p_root->p_edge);
   
    return p_root;
    
}


//Create a new node in the tree from an edge.
node_t *node_create(node_t *p_parent, int select, repo_t* p_repo){
    
    //TODO: EDGE AND RECORD REPO.
    
    node_t *p_child = node_repo_add(p_repo->sp_node_repo);
    p_parent->p_edge->p_child = p_child;
    
    edge_t* p_edge_parent = (p_parent->p_edge) + select;
    if(p_edge_parent->pass_flag){
        p_child->p_move = NULL ;
        p_child->npass = p_parent->npass +1;
    }else{
        p_child->p_move = &(p_edge_parent->move);
        p_child->npass = 0;
    }
    
    p_child->p_parent = p_parent;
    p_child->nchildren = 0;
    p_child->total_visit = 0;
    p_child->round = p_parent->round + 1;
    
  
    
    predict_t predict_result;
    predict_t *p_predict = &predict_result;
    
    p_child->npredict = p_predict->nmove;
    p_child->p_edge = edge_repo_add(p_repo->sp_edge_repo);
    p_child->winrate = p_predict->winrate;
    edge_init(p_predict,p_child->p_edge);
   
    return p_child;
}

node_t *mcts_init(repo_t* p_repo){
    
    node_t *head = node_init(p_repo);

    return head;
}
void call_Pyfunc(PyObject *func, int x[19][19], int y,predict_t *p_predict) {
PyObject *args;
PyObject *kwargs;
PyObject *result=0;
double retval;

/* Make sure we own the GIL */
PyGILState_STATE state = PyGILState_Ensure();

/* Verify that func is a proper callable */
if (!PyCallable_Check(func)) {
  fprintf(stderr,"call_func: expected a callable\n");
  goto fail;
}
      /* Build arguments */
    
args = Py_BuildValue("(((iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii)(iiiiiiiiiiiiiiiiiii))(i))",x[0][0],x[0][1],x[0][2],x[0][3],x[0][4],x[0][5],x[0][6],x[0][7],x[0][8],x[0][9],x[0][10],x[0][11],x[0][12],x[0][13],x[0][14],x[0][15],x[0][16],x[0][17],x[0][18],x[1][0],x[1][1],x[1][2],x[1][3],x[1][4],x[1][5],x[1][6],x[1][7],x[1][8],x[1][9],x[1][10],x[1][11],x[1][12],x[1][13],x[1][14],x[1][15],x[1][16],x[1][17],x[1][18],x[2][0],x[2][1],x[2][2],x[2][3],x[2][4],x[2][5],x[2][6],x[2][7],x[2][8],x[2][9],x[2][10],x[2][11],x[2][12],x[2][13],x[2][14],x[2][15],x[2][16],x[2][17],x[2][18],x[3][0],x[3][1],x[3][2],x[3][3],x[3][4],x[3][5],x[3][6],x[3][7],x[3][8],x[3][9],x[3][10],x[3][11],x[3][12],x[3][13],x[3][14],x[3][15],x[3][16],x[3][17],x[3][18],x[4][0],x[4][1],x[4][2],x[4][3],x[4][4],x[4][5],x[4][6],x[4][7],x[4][8],x[4][9],x[4][10],x[4][11],x[4][12],x[4][13],x[4][14],x[4][15],x[4][16],x[4][17],x[4][18],x[5][0],x[5][1],x[5][2],x[5][3],x[5][4],x[5][5],x[5][6],x[5][7],x[5][8],x[5][9],x[5][10],x[5][11],x[5][12],x[5][13],x[5][14],x[5][15],x[5][16],x[5][17],x[5][18],x[6][0],x[6][1],x[6][2],x[6][3],x[6][4],x[6][5],x[6][6],x[6][7],x[6][8],x[6][9],x[6][10],x[6][11],x[6][12],x[6][13],x[6][14],x[6][15],x[6][16],x[6][17],x[6][18],x[7][0],x[7][1],x[7][2],x[7][3],x[7][4],x[7][5],x[7][6],x[7][7],x[7][8],x[7][9],x[7][10],x[7][11],x[7][12],x[7][13],x[7][14],x[7][15],x[7][16],x[7][17],x[7][18],x[8][0],x[8][1],x[8][2],x[8][3],x[8][4],x[8][5],x[8][6],x[8][7],x[8][8],x[8][9],x[8][10],x[8][11],x[8][12],x[8][13],x[8][14],x[8][15],x[8][16],x[8][17],x[8][18],x[9][0],x[9][1],x[9][2],x[9][3],x[9][4],x[9][5],x[9][6],x[9][7],x[9][8],x[9][9],x[9][10],x[9][11],x[9][12],x[9][13],x[9][14],x[9][15],x[9][16],x[9][17],x[9][18],x[10][0],x[10][1],x[10][2],x[10][3],x[10][4],x[10][5],x[10][6],x[10][7],x[10][8],x[10][9],x[10][10],x[10][11],x[10][12],x[10][13],x[10][14],x[10][15],x[10][16],x[10][17],x[10][18],x[11][0],x[11][1],x[11][2],x[11][3],x[11][4],x[11][5],x[11][6],x[11][7],x[11][8],x[11][9],x[11][10],x[11][11],x[11][12],x[11][13],x[11][14],x[11][15],x[11][16],x[11][17],x[11][18],x[12][0],x[12][1],x[12][2],x[12][3],x[12][4],x[12][5],x[12][6],x[12][7],x[12][8],x[12][9],x[12][10],x[12][11],x[12][12],x[12][13],x[12][14],x[12][15],x[12][16],x[12][17],x[12][18],x[13][0],x[13][1],x[13][2],x[13][3],x[13][4],x[13][5],x[13][6],x[13][7],x[13][8],x[13][9],x[13][10],x[13][11],x[13][12],x[13][13],x[13][14],x[13][15],x[13][16],x[13][17],x[13][18],x[14][0],x[14][1],x[14][2],x[14][3],x[14][4],x[14][5],x[14][6],x[14][7],x[14][8],x[14][9],x[14][10],x[14][11],x[14][12],x[14][13],x[14][14],x[14][15],x[14][16],x[14][17],x[14][18],x[0][0],x[0][1],x[0][2],x[0][3],x[0][4],x[0][5],x[0][6],x[0][7],x[0][8],x[0][9],x[0][10],x[0][11],x[0][12],x[0][13],x[0][14],x[0][15],x[0][16],x[0][17],x[0][18],x[15][0],x[15][1],x[15][2],x[15][3],x[15][4],x[15][5],x[15][6],x[15][7],x[15][8],x[15][9],x[15][10],x[15][11],x[15][12],x[15][13],x[15][14],x[15][15],x[15][16],x[15][17],x[15][18],x[16][0],x[16][1],x[16][2],x[16][3],x[16][4],x[16][5],x[16][6],x[16][7],x[16][8],x[16][9],x[16][10],x[16][11],x[16][12],x[16][13],x[16][14],x[16][15],x[16][16],x[16][17],x[16][18],x[17][0],x[17][1],x[17][2],x[17][3],x[17][4],x[17][5],x[17][6],x[17][7],x[17][8],x[17][9],x[17][10],x[17][11],x[17][12],x[17][13],x[17][14],x[17][15],x[17][16],x[17][17],x[17][18],x[18][0],x[18][1],x[18][2],x[18][3],x[18][4],x[18][5],x[18][6],x[18][7],x[18][8],x[18][9],x[18][10],x[18][11],x[18][12],x[18][13],x[18][14],x[18][15],x[18][16],x[18][17],x[18][18],y);
        
        
    kwargs = NULL;

      /* Call the function */
    result = PyObject_Call(func, args, kwargs);
    Py_DECREF(args);
    Py_XDECREF(kwargs);

    /* Check for Python exceptions (if any) */
    if (PyErr_Occurred()) {
    PyErr_Print();
    goto fail;
    }

    /* Verify the result is a float object */
    if (!PyTuple_Check(result)) {
    fprintf(stderr,"call_func: callable didn't return a tuple\n");
    goto fail;
    }
      
      /* Create the return value */
    //  retval = PyFloat_AsDouble(result);
     // Py_DECREF(result);

      /* Restore previous GIL state and return */
    PyGILState_Release(state);
     // return retval;
    

    fail:
      Py_XDECREF(result);
      PyGILState_Release(state);
      abort();   // Change to something more appropriate
    }

PyObject *import_name(const char *modname, const char *symbol) {
    PyObject *u_name, *module;
    u_name = PyUnicode_FromString(modname);
    module = PyImport_Import(u_name);
    Py_DECREF(u_name);
    return PyObject_GetAttrString(module, symbol);
}

    

void mcts_search(node_t *p_search, estack_t* p_stack, repo_t* p_repo,int c){
    
    int extend_flag = 0;
    stack_push(p_stack, p_search);
    int search_depth =0;
    while(!extend_flag && p_search->npass < 2){
        p_search->total_visit += 1;
        int next_index = max_priority(p_search, c, search_depth);
        
        if(p_search->p_edge[next_index].nvisit++){
            p_search = p_search->p_edge[next_index].p_child;
        }else{
            p_search = node_create(p_search, next_index, p_repo);
            extend_flag = 1;
        }
        
        stack_push(p_stack, p_search);
        search_depth += 1;
    }
    
}

void mcts_backup(estack_t* p_stack){
    
    int empty_flag = is_empty_stack(p_stack);
    node_t** pp;
    node_t* p_backup;
    
    while(!empty_flag){
        
        stack_pop(p_stack, pp);
        p_backup = *pp;
        
        if(p_backup->p_parent!=NULL && !(p_backup->round%2) && p_backup->p_parent->winrate > p_backup->winrate){
            p_backup->p_parent->winrate = p_backup->winrate;
        }else if(p_backup->p_parent!=NULL && p_backup->round%2 && p_backup->p_parent->winrate < p_backup->winrate){
            p_backup->p_parent->winrate = p_backup->winrate;
        }
        
        empty_flag = is_empty_stack(p_stack);
        
    }
    
}

//Make one move after searching the tree.
node_t *mcts_move(node_t* p_head, int n_search, repo_t *p_repo, int c){
    
    estack_t* p_stack = stack_init(MAXSTACKSIZE);
    
    int i = 0;
    for(;i<n_search;i++){
        mcts_search(p_head, p_stack, p_repo,c);
        mcts_backup(p_stack);
    }
    int next_index=max_priority(p_head, c, -1);
    stack_free(p_stack);
    return p_head->p_edge[next_index].p_child;
}



// Play one game.
void mcts(int n_search, int c){
    repo_t *p_repo;
    repo_init(p_repo);
    
    node_t *p_head = mcts_init(p_repo);
    
    node_t *p_search = p_head;
    
 
    int end_flag = 0;
    while(!end_flag && p_search->round < MAXMOVE){
        p_search = mcts_move(p_search, n_search, p_repo,c);
        
        
        assert(p_search->p_parent != NULL);
        end_flag = p_search->npass == 2 ? 1 : 0;
    }
    int winner = win(p_search->p_record);
    FILE *fp;
    fp = fopen("testset.dat","a");
    node_t* p_dataset = p_search;
    int head_flag =0;
    while(!head_flag){
        if(p_dataset->p_parent != NULL){
            node_t* p_temp = p_dataset;
            p_dataset = p_dataset->p_parent;
            record_t* p_rec = p_dataset->p_record;
            char sample[SAMPLESIZE];
            int index=0;
            int i =0;
            for(;i<BOARDSIZE;i++){
                int j=0;
                for(;j<BOARDSIZE;j++){
                    sample[index++] = p_rec->board[i][j] + '1';
                    sample[index++] = ',';
                }
            }
            sample[index-1] = ';';
            
            if((p_rec->round)%2)
                sample[index]= '1';
            else{
                sample[index]= '0';
            }
            index += 1;
            sample[index++] = ';';
            sample[index++] = winner;
            sample[index++] = '\n';
            sample[index] = '\0';
            if(p_temp->p_move != NULL){
               sample[38*(*(p_temp->p_move)[0])+2*(*(p_temp->p_move)[1])] = '3';
            }
            fwrite(sample,sizeof(sample)-1,1,fp);
        }else{
            head_flag = 1;
        }
    }
    
    fclose(fp);
    
    repo_free(p_repo);
    
}
