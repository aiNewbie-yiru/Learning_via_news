import sys

from app.services.vocab_enhancer import FALLBACK_DEFINITIONS, VocabEnhancerService


def main() -> int:
    service = VocabEnhancerService()
    result = service.enhance_word(
        "interim",
        "CET6",
        article_context="The government has hit an interim target for speeding up hospital treatment in England.",
    )

    print(result)

    fallback_values = set(FALLBACK_DEFINITIONS.values())
    if result.get("definition") in fallback_values:
        print("ERROR: vocabulary enhancer returned fallback definition")
        return 1

    if not result.get("definition_cn"):
        print("ERROR: vocabulary enhancer did not return Chinese definition")
        return 1

    if not result.get("example_sentence_2"):
        print("ERROR: vocabulary enhancer did not return second example sentence")
        return 1

    print("Vocabulary API check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
