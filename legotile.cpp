#include <bits/stdc++.h>
using namespace std;
#define rep(i, from, to) for (int i = from; i < (to); ++i)
typedef long long ll;
typedef long double ld;
typedef unsigned long long ull;
typedef vector<int> vi;
typedef pair<int,int> ii;
typedef vector<pair<int, int>> vii;

int s, h;

// A point. Shorter syntax than pair.
struct pnt {
    int i, j;
    void next() {
        j += 1;
        if (j == s) {
            j = 0;
            i += 1;
        }
    }
};

struct Layer {
    // A grid of 0s and 1s. 1s indicate which spots should be filled with lego bricks
    vector<vi> remaining;
    // A grid of 0s and 1s and then a a lot of negative integers. 0s indicate free spots, 1s indicate to-be-built spots,
    // and the negative integers indicate built spots, with its absolute value signifying which brick covers the spot
    vector<vi> all;
    // The penalty, which is calculated from the crevices shared with the layer below
    // It is sorted by the penalty
    int penalty;
    // Coordinate pair for where we the last lower-left 1-corner was
    pnt lastcorner;
    // number of bricks
    int num_bricks;
};

struct Crevice {
    int up, down, left, right;
};


struct UF {

    int n;
    vi rank;
    vi p;

    UF(int nn) {
        n = nn;
        rank.assign(n, 0);
        rep(i,0,n)
            p.push_back(i);
    }

    int find(int a) {
        if (p[a] != a)
            p[a] = find(p[a]);
        return p[a];
    }

    void uni(int a, int b) {
        int pa = find(a);
        int pb = find(b);

        if (rank[pa] < rank[pb]) {
            p[pa] = pb;
        } else {
            p[pb] = pa;
            if (rank[pa] == rank[pb]) {
                rank[pa]++;
            }
        }
    }
};

int uf_index(int i, int j) {
    return s*i+j;
}

        


int calculate_connected_components(vector<vi>& layer1, vector<vi>& layer2) {
    // use a unionfind
    UF uf = UF(uf_index(s,s));
    // we use layer2 to check the number of components later
    map<int, int> layer1m;
    rep(i,0,s) rep(j,0,s) {
        if (layer1[i][j] != 0) {
            auto f = layer1m.find(layer1[i][j]);
            if (f != layer1m.end()) {
                uf.uni(uf_index(i,j), f->second);
            } else {
                layer1m.insert(make_pair(layer1[i][j], uf_index(i,j)));
            }
        }
    }
    map<int, int> layer2m;
    rep(i,0,s) rep(j,0,s) {
        if (layer2[i][j] != 0) {
            auto f = layer2m.find(layer2[i][j]);
            if (f != layer2m.end()) {
                uf.uni(uf_index(i,j), f->second);
            } else {
                layer2m.insert(make_pair(layer2[i][j], uf_index(i,j)));
            }
        }
    }

    // now, we have unioned all bricks
    // check how many different components we have in layer2
    set<int> components;
    rep(i,0,s) rep(j,0,s) {
        if (layer2[i][j]) {
            components.insert(uf.find(uf_index(i,j)));
        }
    }
    return components.size();

}

int all_calculate_connected_components(vector<vector<vi>>& layers, vector<vi>& layer2) {
    // use a unionfind
    UF uf = UF(uf_index(s,s));
    // we use layer2 to check the number of components later
    for (auto& layer1 : layers) {
        map<int, int> layer1m;
        rep(i,0,s) rep(j,0,s) {
            if (layer1[i][j] != 0) {
                auto f = layer1m.find(layer1[i][j]);
                if (f != layer1m.end()) {
                    uf.uni(uf_index(i,j), f->second);
                } else {
                    layer1m.insert(make_pair(layer1[i][j], uf_index(i,j)));
                }
            }
        }
    }
    map<int, int> layer2m;
    rep(i,0,s) rep(j,0,s) {
        if (layer2[i][j] != 0) {
            auto f = layer2m.find(layer2[i][j]);
            if (f != layer2m.end()) {
                uf.uni(uf_index(i,j), f->second);
            } else {
                layer2m.insert(make_pair(layer2[i][j], uf_index(i,j)));
            }
        }
    }

    // now, we have unioned all bricks
    // check how many different components we have in layer2
    set<int> components;
    rep(i,0,s) rep(j,0,s) {
        if (layer2[i][j]) {
            components.insert(uf.find(uf_index(i,j)));
        }
    }
    return components.size();

}



int main()
{
    ios::sync_with_stdio(false);
    cin.tie(0);
    cin.exceptions(cin.failbit);

    // input will consist of:
    // one row with s and h
    // then h chuncks of s rows with s integers (-1, 0 or 1)
    // we assume the first layer is the bottom-most layer
    // we assume s >= 3
    cin >> s >> h;

    vector<vector<vi>> original_matrix(h, vector<vi>(s, vi(s)));

    rep(layer,0,h) {
        rep(i,0,s) rep(j,0,s) {
            cin >> original_matrix[layer][i][j];
        }
    }

    // if we want a solid structure, just convert all -1s into 1s
    bool solid = false;
    if (solid) {
        rep(l,0,h) rep(i,0,s) rep(j,0,s) {
            if (original_matrix[l][i][j] == -1) original_matrix[l][i][j] = 1;
        }
    }


    // Now, convert all -1s that we KNOW are 1s
    rep(l,0,h) rep(i,0,s) rep(j,0,s) {
        if (original_matrix[l][i][j] == 1) {
            if (i > 0) {
                if (original_matrix[l][i-1][j] == 0) original_matrix[l][i+1][j] = 1;
            } else {
                original_matrix[l][i+1][j] = 1;
            }
            if (i < s-1) {
                if (original_matrix[l][i+1][j] == 0) original_matrix[l][i-1][j] = 1;
            } else {
                original_matrix[l][i-1][j] = 1;
            }
            if (j > 0) {
                if (original_matrix[l][i][j-1] == 0) original_matrix[l][i][j+1] = 1;
            } else {
                original_matrix[l][i][j+1] = 1;
            }
            if (j < s-1) {
                if (original_matrix[l][i][j+1] == 0) original_matrix[l][i][j-1] = 1;
            } else {
                original_matrix[l][i][j-1] = 1;
            }
        }
    }

    // TODO: if we have at one xy position, and no zeroes below it, make the entire column beneath it consist of only 1s
    // this will make pyramid structure worse, but other structures better

    // turn all remaining -1s into zeroes
    rep(l,0,h) rep(i,0,s) rep(j,0,s) {
        if (original_matrix[l][i][j] == -1) original_matrix[l][i][j] = 0;
    }

    // Print our original matrix
    /*cout << "ORIGINAL MATRIX:" << endl;
    rep(l,0,h) {
        rep(i,0,s) {
            rep(j,0,s) {
                cout << original_matrix[l][i][j] << " ";
            }
            cout << endl;
        }
        cout << endl;
    }
    cout << "END OF ORIGINAL MATRIX" << endl;*/


    // The finalmatrix, yet to be filled
    vector<vector<vi>> final_matrix;

    // we save the last crevices layer
    // it contains penalty per crevice
    // (penalty is 10 if crevice existed in previous layer, and 50 if it existed in the two preceding layers)
    // (penalty increases by 1 for each 2x2 brick)
    // initially, the crevice layer is all 0s. this makes sure the first layer is realtively fast
    vector<vector<Crevice>> crevice_layer(s, vector<Crevice>(s, {0,0,0,0}));

    // We now iterate over each layer
    rep(l, 0, h) {

        // create the set of layers, which we will use as a priority queue which supports removal
        // similar to dijkstra
        set<pair<int, vector<vi>>> layer_queue;
        // for each layer, save the current penalty
        map<vector<vi>, int> layer_penalty;
        // for each layer, also store the currently best Layer
        map<vector<vi>, Layer> best_layer;

        // The initial layer is exactly the layer from original_matrix
        Layer initial_layer;
        initial_layer.remaining = original_matrix[l];
        initial_layer.all = original_matrix[l];
        initial_layer.penalty = 0;
        initial_layer.lastcorner = {0, 0};
        initial_layer.num_bricks = 0;

        /*cout << "initial layer:" << endl;
        rep(i,0,s) {
            rep(j,0,s) {
                cout << initial_layer.all[i][j] << " ";
            }
            cout << endl;
        }
        cout << "end of initial layer" << endl;*/


        // add the initial_layer to our queue
        layer_queue.insert(make_pair(initial_layer.penalty, initial_layer.remaining));
        layer_penalty.insert(make_pair(initial_layer.remaining, initial_layer.penalty));
        best_layer.insert(make_pair(initial_layer.remaining, initial_layer));

        Layer chosen_layer;

        // iterate until our queue is empty (or, more likely, we have found an optimal solution and have breaked before that)
        while (!layer_queue.empty()) {
           // take the first layer, that is, the one with the least penalty
            pair<int, vector<vi>> current_pair = *layer_queue.begin();
            layer_queue.erase(layer_queue.begin());

            // Get the best layer
            Layer current_layer = best_layer[current_pair.second];

            // now, find the next corner
            pnt lastcorner = current_layer.lastcorner;
            // we start by looping from the lastcorner
            while (lastcorner.i < s) {
                // check if this is a 1
                if (current_layer.remaining[lastcorner.i][lastcorner.j] == 1) {
                    // BREAK;
                    break;
                }
                lastcorner.next();
            }
            if (lastcorner.i == s) {
                // YAY WE FOUND IT
                // THIS IS OUR LAYER
                //cout << "WE CHOSE A LAYER" << endl;
                chosen_layer = current_layer;
                break;
            }

            // increase number of bricks
            current_layer.num_bricks += 1;
            current_layer.lastcorner = lastcorner;

            // We have three ways in which we can place bricks: 4x2, 2x4 and 2x2
            // Try them all
            if (lastcorner.i <= s-4 && lastcorner.j <= s-2) {
                // try 4x2
                bool works = true;
                rep(i, lastcorner.i, lastcorner.i+4) rep(j, lastcorner.j, lastcorner.j+2) {
                    if (current_layer.remaining[i][j] != 1) works = false;
                }
                if (works) {
                    // calculate the crevice penalty
                    int add_penalty = 0;
                    rep(i,lastcorner.i,lastcorner.i+4) {
                        add_penalty += crevice_layer[i][lastcorner.j].left;
                        add_penalty += crevice_layer[i][lastcorner.j+1].right;
                    }
                    rep(j,lastcorner.j,lastcorner.j+2) {
                        add_penalty += crevice_layer[lastcorner.i][j].down;
                        add_penalty += crevice_layer[lastcorner.i+3][j].up;
                    }
                    // copy current_layer
                    Layer new_layer = current_layer;
                    new_layer.penalty += add_penalty;
                    // modify 1s into 0s and -num_bricks
                    rep(i, lastcorner.i, lastcorner.i+4) rep(j, lastcorner.j, lastcorner.j+2) {
                        new_layer.remaining[i][j] = 0;
                        int unique_id = 1000000  + new_layer.num_bricks;
                        new_layer.all[i][j] = -unique_id;
                    }
                    // we're finished with this layer now
                    // check if we're good or not
                    auto exist_layer = layer_penalty.find(new_layer.remaining);
                    if (exist_layer != layer_penalty.end()) {
                        // check if greater
                        if (exist_layer->second > new_layer.penalty) {
                            // CHANGE BEST ONE
                            layer_queue.erase(make_pair(exist_layer->second, exist_layer->first));
                            layer_penalty[new_layer.remaining] = new_layer.penalty;
                            layer_queue.insert(make_pair(new_layer.penalty, new_layer.remaining));
                            best_layer[new_layer.remaining] = new_layer;
                        }
                        if (exist_layer->second == new_layer.penalty && l > 0) {
                            //  CHOOSE THE ONE WITH FEWEST CONNECTED COMPONENTS
                            // calculate the number of connected components using unionfind
                            int new_connected_components = calculate_connected_components(final_matrix[final_matrix.size()-1], new_layer.all);
                            int exist_connected_components = calculate_connected_components(final_matrix[final_matrix.size()-1], best_layer[new_layer.remaining].all);
                            int new_all_connected_components = all_calculate_connected_components(final_matrix, new_layer.all);
                            int exist_all_connected_components = all_calculate_connected_components(final_matrix, best_layer[new_layer.remaining].all);
                            if (new_connected_components < exist_connected_components || (new_connected_components == exist_connected_components && new_all_connected_components < exist_all_connected_components)) {
                                // Choose our new layer
                                layer_queue.erase(make_pair(exist_layer->second, exist_layer->first));
                                layer_penalty[new_layer.remaining] = new_layer.penalty;
                                layer_queue.insert(make_pair(new_layer.penalty, new_layer.remaining));
                                best_layer[new_layer.remaining] = new_layer;
                            }
                        }

                    } else {
                        // add to everything
                        layer_penalty.insert(make_pair(new_layer.remaining, new_layer.penalty));
                        layer_queue.insert(make_pair(new_layer.penalty, new_layer.remaining));
                        best_layer.insert(make_pair(new_layer.remaining, new_layer));
                    }
                    // THAT'S IT
                }
            }
            if (lastcorner.i <= s-2 && lastcorner.j <= s-4) {
                // try 2x4
                bool works = true;
                rep(i, lastcorner.i, lastcorner.i+2) rep(j, lastcorner.j, lastcorner.j+4) {
                    if (current_layer.remaining[i][j] != 1) works = false;
                }
                if (works) {
                    // calculate the crevice penalty
                    int add_penalty = 0;
                    rep(i,lastcorner.i,lastcorner.i+2) {
                        add_penalty += crevice_layer[i][lastcorner.j].left;
                        add_penalty += crevice_layer[i][lastcorner.j+3].right;
                    }
                    rep(j,lastcorner.j,lastcorner.j+4) {
                        add_penalty += crevice_layer[lastcorner.i][j].down;
                        add_penalty += crevice_layer[lastcorner.i+1][j].up;
                    }
                    // copy current_layer
                    Layer new_layer = current_layer;
                    new_layer.penalty += add_penalty;
                    // modify 1s into 0s and -num_bricks
                    rep(i, lastcorner.i, lastcorner.i+2) rep(j, lastcorner.j, lastcorner.j+4) {
                        new_layer.remaining[i][j] = 0;
                        // Create a unique ID. The ID should be easily distinguishable from 4x2 and 2x4
                        int unique_id = 2000000  + new_layer.num_bricks;
                        new_layer.all[i][j] = -unique_id;
                    }
                    // we're finished with this layer now
                    // check if we're good or not
                    auto exist_layer = layer_penalty.find(new_layer.remaining);
                    if (exist_layer != layer_penalty.end()) {
                        // check if greater
                        if (exist_layer->second > new_layer.penalty) {
                            // CHANGE BEST ONE
                            layer_queue.erase(make_pair(exist_layer->second, exist_layer->first));
                            layer_penalty[new_layer.remaining] = new_layer.penalty;
                            layer_queue.insert(make_pair(new_layer.penalty, new_layer.remaining));
                            best_layer[new_layer.remaining] = new_layer;
                        }
                        if (exist_layer->second == new_layer.penalty && l > 0) {
                            //  CHOOSE THE ONE WITH FEWEST CONNECTED COMPONENTS
                            // calculate the number of connected components using unionfind
                            int new_connected_components = calculate_connected_components(final_matrix[final_matrix.size()-1], new_layer.all);
                            int exist_connected_components = calculate_connected_components(final_matrix[final_matrix.size()-1], best_layer[new_layer.remaining].all);
                            int new_all_connected_components = all_calculate_connected_components(final_matrix, new_layer.all);
                            int exist_all_connected_components = all_calculate_connected_components(final_matrix, best_layer[new_layer.remaining].all);
                            if (new_connected_components < exist_connected_components || (new_connected_components == exist_connected_components && new_all_connected_components < exist_all_connected_components)) {
                                // Choose our new layer
                                layer_queue.erase(make_pair(exist_layer->second, exist_layer->first));
                                layer_penalty[new_layer.remaining] = new_layer.penalty;
                                layer_queue.insert(make_pair(new_layer.penalty, new_layer.remaining));
                                best_layer[new_layer.remaining] = new_layer;
                            }
                        }
                    } else {
                        // add to everything
                        layer_penalty.insert(make_pair(new_layer.remaining, new_layer.penalty));
                        layer_queue.insert(make_pair(new_layer.penalty, new_layer.remaining));
                        best_layer.insert(make_pair(new_layer.remaining, new_layer));
                    }
                    // THAT'S IT
                }
            }
            if (lastcorner.i <= s-2 && lastcorner.j <= s-2) {
                // try 2x2
                bool works = true;
                rep(i, lastcorner.i, lastcorner.i+2) rep(j, lastcorner.j, lastcorner.j+2) {
                    if (current_layer.remaining[i][j] != 1) works = false;
                }
                if (works) {
                    // calculate the crevice penalty
                    // PENALTY STARTS AT 1 SINCE WE ARE USING 2X2 BRICK
                    int add_penalty = 1;
                    rep(i,lastcorner.i,lastcorner.i+2) {
                        add_penalty += crevice_layer[i][lastcorner.j].left;
                        add_penalty += crevice_layer[i][lastcorner.j+1].right;
                    }
                    rep(j,lastcorner.j,lastcorner.j+2) {
                        add_penalty += crevice_layer[lastcorner.i][j].down;
                        add_penalty += crevice_layer[lastcorner.i+1][j].up;
                    }
                    // copy current_layer
                    Layer new_layer = current_layer;
                    new_layer.penalty += add_penalty;
                    // modify 1s into 0s and -num_bricks
                    rep(i, lastcorner.i, lastcorner.i+2) rep(j, lastcorner.j, lastcorner.j+2) {
                        new_layer.remaining[i][j] = 0;
                        // Create a unique ID. The ID should be easily distinguishable from 4x2 and 2x4
                        int unique_id = 3000000  + new_layer.num_bricks;
                        new_layer.all[i][j] = -unique_id;
                    }
                    // we're finished with this layer now
                    // check if we're good or not
                    auto exist_layer = layer_penalty.find(new_layer.remaining);
                    if (exist_layer != layer_penalty.end()) {
                        // check if greater
                        if (exist_layer->second > new_layer.penalty) {
                            // CHANGE BEST ONE
                            layer_queue.erase(make_pair(exist_layer->second, exist_layer->first));
                            layer_penalty[new_layer.remaining] = new_layer.penalty;
                            layer_queue.insert(make_pair(new_layer.penalty, new_layer.remaining));
                            best_layer[new_layer.remaining] = new_layer;
                        }
                        if (exist_layer->second == new_layer.penalty && l > 0) {
                            //  CHOOSE THE ONE WITH FEWEST CONNECTED COMPONENTS
                            // calculate the number of connected components using unionfind
                            int new_connected_components = calculate_connected_components(final_matrix[final_matrix.size()-1], new_layer.all);
                            int exist_connected_components = calculate_connected_components(final_matrix[final_matrix.size()-1], best_layer[new_layer.remaining].all);
                            int new_all_connected_components = all_calculate_connected_components(final_matrix, new_layer.all);
                            int exist_all_connected_components = all_calculate_connected_components(final_matrix, best_layer[new_layer.remaining].all);
                            if (new_connected_components < exist_connected_components || (new_connected_components == exist_connected_components && new_all_connected_components < exist_all_connected_components)) {
                                // Choose our new layer
                                layer_queue.erase(make_pair(exist_layer->second, exist_layer->first));
                                layer_penalty[new_layer.remaining] = new_layer.penalty;
                                layer_queue.insert(make_pair(new_layer.penalty, new_layer.remaining));
                                best_layer[new_layer.remaining] = new_layer;
                            }
                        }
                    } else {
                        // add to everything
                        layer_penalty.insert(make_pair(new_layer.remaining, new_layer.penalty));
                        layer_queue.insert(make_pair(new_layer.penalty, new_layer.remaining));
                        best_layer.insert(make_pair(new_layer.remaining, new_layer));
                    }
                    // THAT'S IT
                }
            }
        }

        //cout << "AFTER CHOSEN LAYER. IF NOT, THEN BAD" << endl;

        // convert our chosen layer into positive integers again, now where there should be no 1s
        rep(i,0,s) rep(j,0,s) {
            chosen_layer.all[i][j] = -chosen_layer.all[i][j];
            assert(chosen_layer.all[i][j] >= 0);
        }



        /*cout << "our chosen layer:" << endl;
        rep(i,0,s) {
            rep(j,0,s) {
                cout << chosen_layer.all[i][j] << " ";
            }
            cout << endl;
        }
        cout << "end of our chosen layer" << endl;*/


        // now, we have chosen a layer
        // this is reallly really really good
        //  what do we do now?
        // we add the layer to our final-layers, and update the crevice information
        final_matrix.push_back(chosen_layer.all);

        // now create the new crevice layer
        vector<vector<Crevice>> new_crevice_layer(s, vector<Crevice>(s, {0,0,0,0}));

        // Scan the chosen layer
        // for every non-zero, check if we have a non-zero neighbor, and if so, add that to the crevice information
        // also check compare with last crevice – penalty is then multiplied by 5
        rep(i,0,s) rep(j,0,s) {
            if (chosen_layer.all[i][j] == 0) continue;
            if (i > 0) {
                if (chosen_layer.all[i-1][j] != 0 && chosen_layer.all[i-1][j] != chosen_layer.all[i][j]) {
                    // WE FOUND A CREVICE
                    new_crevice_layer[i][j].down = 10;
                }
                if (crevice_layer[i][j].down != 0) new_crevice_layer[i][j].down *= 5;
            }
            if (i < s-1) {
                if (chosen_layer.all[i+1][j] != 0 && chosen_layer.all[i+1][j] != chosen_layer.all[i][j]) {
                    // WE FOUND A CREVICE
                    new_crevice_layer[i][j].up = 10;
                }
                if (crevice_layer[i][j].up != 0) new_crevice_layer[i][j].up *= 5;
            }
            if (j > 0) {
                if (chosen_layer.all[i][j-1] != 0 && chosen_layer.all[i][j-1] != chosen_layer.all[i][j]) {
                    // WE FOUND A CREVICE
                    new_crevice_layer[i][j].left = 10;
                }
                if (crevice_layer[i][j].left != 0) new_crevice_layer[i][j].left *= 5;
            }
            if (j < s-1) {
                if (chosen_layer.all[i][j+1] != 0 && chosen_layer.all[i][j+1] != chosen_layer.all[i][j]) {
                    // WE FOUND A CREVICE
                    new_crevice_layer[i][j].right = 10;
                }
                if (crevice_layer[i][j].right != 0) new_crevice_layer[i][j].right *= 5;
            }
        }

        // now make the new crevice layer the old one
        crevice_layer = new_crevice_layer;

        // FINISHED

    }



    // ALL LAYERS DONE
    // WOHOO

    /*cout << endl << endl;
    cout << "FINAL RESULTS" << endl << endl;

    // Print them
    rep(l,0,h) {
        rep(i,0,s) {
            rep(j,0,s) {
                cout << final_matrix[l][i][j] << " ";
            }
            cout << endl;
        }
        cout << endl;
    }*/


    // Now create build instructions based on the layers
    // The build instructions take the format TYPE X Y Z, e.g. 2x4 0 1 0
    // The X Y Z coordinates siginify the lower left corner of the brick
    // One instruction per row
    rep(l,0,h) rep(i,0,s) rep(j,0,s) {
        if (final_matrix[l][i][j] != 0) {
            int type = final_matrix[l][i][j] / 1000000;
            if (type == 1) {
                // it's 4x2
                cout << "4x2 " << i << " " << j << " " << l << endl;
                // Turn all other into 0s
                rep(ic,i,i+4) rep(jc,j,j+2) {
                    final_matrix[l][ic][jc] = 0;
                }
            } else if (type == 2) {
                // 2x4
                cout << "2x4 " << i << " " << j << " " << l << endl;
                // Turn all other into 0s
                rep(ic,i,i+2) rep(jc,j,j+4) {
                    final_matrix[l][ic][jc] = 0;
                }
            } else if (type == 3) {
                // 2x4
                cout << "2x2 " << i << " " << j << " " << l << endl;
                // Turn all other into 0s
                rep(ic,i,i+2) rep(jc,j,j+2) {
                    final_matrix[l][ic][jc] = 0;
                }
            } else {
                cout << "ERROR" << endl;
                return -1;
            }
        }
    }




    return 0;
}
