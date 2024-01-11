import chain
import sys
import vectordb

from langchain_community.vectorstores import Chroma


def test_vectorstore_text() -> Chroma:
    input_text = """
    The rock parrot (Neophema petrophila) is a species of grass parrot native to Australia. Described by John Gould in 1841, it is a small parrot 22–24 cm (8+3⁄4–9+1⁄2 in) long and weighing 50–60 g (1+3⁄4–2 oz) with predominantly olive-brown upperparts and more yellowish underparts. Its head is olive with light blue forecheeks and lores, and a dark blue frontal band line across the crown with lighter blue above and below. The sexes are similar in appearance, although the female tends to have a duller frontal band and less blue on the face. The female's call also tends to be far louder and more shrill than the male's. Two subspecies are currently recognised.

    Rocky islands and coastal dune areas are the preferred habitats for this species, which is found from Lake Alexandrina in southeastern South Australia westwards across coastal South and Western Australia to Shark Bay. Unlike other grass parrots, it nests in burrows or rocky crevices mostly on offshore islands such as Rottnest Island. Seeds of grasses and succulent plants form the bulk of its diet. The species has suffered in the face of feral mammals; although its population is declining, it is considered to be a least-concern species by the International Union for Conservation of Nature (IUCN).

    Taxonomy
    The rock parrot was described by the English ornithologist John Gould in 1841 as Euphema petrophila,[2] its specific name petrophila derived from the Ancient Greek πετρος (petros) 'rock' and φιλος (philos) 'loving'.[3] The author's specimen was one of fifty new bird species presented before the Zoological Society of London.[2] The rock parrot was included in Gould's fifth volume of Birds of Australia, using specimens obtained at Port Lincoln in South Australia and from collector John Gilbert in Western Australia. Gilbert stated that at the time of English colonisation the species was common on cliff faces on offshore islands, including Rottnest, near the western port of Fremantle, the nests in almost inaccessible locations.[4]

    The Italian ornithologist Tommaso Salvadori defined the new genus Neophema in 1891, placing the rock parrot within it and giving it its current scientific name Neophema petrophila.[5] Within the grass parrot genus Neophema, it is one of four species classified in the subgenus Neonanodes.[6] Analysis of mitochondrial DNA published in 2021 indicated the rock parrot is most closely related to the blue-winged parrot, their mutual ancestors most likely diverging between 0.7 and 3.3 million years ago.[7]

    A burrow-nester, the rock parrot has evolved from a lineage of tree-nesting ancestors. The biologist Donald Brightsmith has proposed that several lineages of parrots and trogons switched to nesting in burrows to avoid tree-living mammalian predators that evolved and proliferated in the late Oligocene to early Miocene (30–20 million years ago).[8]

    Two subspecies are recognised by the International Ornithologists' Union: subspecies petrophila from Western Australia and subspecies zietzi from South Australia,[9] the latter described by Gregory Mathews in 1912 from the Sir Joseph Banks Group in Spencer Gulf,[10] after the Assistant Director of the South Australian Museum Amandus Heinrich Christian Zietz.[11] The authors of the online edition of the Handbook of the Birds of the World do not regard this as distinct.[12]

    "Rock parrot" has been designated as the official common name for the species by the International Ornithologists' Union (IOC).[9] Gilbert reported the Swan River colonists called it the rock parrakeet, and he labelled it the rock grass-parrakeet.[4] It is also known as rock elegant parrot.[13]
    """

    return vectordb.create_from_text(input_text)


def test_vectorstore_pdf() -> Chroma:
    return vectordb.create_from_pdf("rock_parrot.pdf")



input_paths = sys.argv[1:]
if len(input_paths) == 0:
    # test data
    input_paths = ["./rock_parrot.pdf"]
    #print("give input file paths as arguments")
    #exit(1)

"""
example question: "When was the rock parrot discovered?"
"""

print("input: " + str.join(", ", input_paths))


# TODO: need to use create() and series of add_pdf() calls 
vectorstore = vectordb.create_from_file(input_paths[0])
retriever = vectorstore.as_retriever()

rag_chain = chain.make_chain(retriever)
print("Enter question: ")
question = input()

my_out = rag_chain.invoke(question)
print("\n")
print("===== output =====")
print(my_out)
print("\n")

